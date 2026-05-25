import React, { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../services/api';
import webSocketService from '../services/websocket';
import './AICopilotDrawer.css';

const STEP_ICONS = {
  'agent:observe': '🔍',
  'agent:analyze': '📊',
  'agent:hypothesis': '💡',
  'agent:patch_generated': '🧬',
  'agent:validation_passed': '🛡️',
  'agent:awaiting_approval': '⏳',
  'agent:deployment_started': '🚀',
  'agent:deployment_completed': '✅',
  'agent:error': '❌',
};

const STEP_LABELS = {
  'agent:observe': 'Observing',
  'agent:analyze': 'Analyzing',
  'agent:hypothesis': 'Hypothesizing',
  'agent:patch_generated': 'Patch Generated',
  'agent:validation_passed': 'Validated',
  'agent:awaiting_approval': 'Awaiting Approval',
  'agent:deployment_started': 'Deploying',
  'agent:deployment_completed': 'Deployed',
  'agent:error': 'Error',
};

export default function AICopilotDrawer({ businessId }) {
  const [isOpen, setIsOpen] = useState(false);
  const [command, setCommand] = useState('');
  const [thoughtLogs, setThoughtLogs] = useState([]);
  const [proposal, setProposal] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [isRollingBack, setIsRollingBack] = useState(false);
  const [versionHistory, setVersionHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('thoughts');
  const logsEndRef = useRef(null);

  // Connect to shared Socket.IO for live thought streaming
  useEffect(() => {
    if (!businessId) return;

    // Ensure the shared websocket is connected, then join agent room
    webSocketService.connect(businessId);
    webSocketService.emit('join_agent_room', { business_id: businessId });

    const handleThoughtLog = (log) => {
      setThoughtLogs((prev) => [...prev, log]);
    };

    webSocketService.on('agent_thought_log', handleThoughtLog);

    return () => {
      webSocketService.off('agent_thought_log', handleThoughtLog);
    };
  }, [businessId]);

  // Auto-scroll thought logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [thoughtLogs]);

  // Fetch version history
  const fetchHistory = useCallback(async () => {
    try {
      const res = await api.get(`/schema/history/${businessId}`);
      if (res.data.success) {
        setVersionHistory(res.data.history || []);
      }
    } catch (err) {
      console.error('Failed to fetch version history:', err);
    }
  }, [businessId]);

  // Run optimization loop
  const handleOptimize = async () => {
    if (!command.trim() || isRunning) return;

    setIsRunning(true);
    setThoughtLogs([]);
    setProposal(null);
    setActiveTab('thoughts');

    try {
      const res = await api.post('/agents/optimize', {
        command: command.trim(),
        business_id: businessId,
      });
      const data = res.data;
      if (data.success) {
        setProposal(data);
        setActiveTab('proposal');
      } else {
        setThoughtLogs((prev) => [
          ...prev,
          {
            event: 'agent:error',
            status: 'error',
            message: data.error || 'Optimization failed.',
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (err) {
      setThoughtLogs((prev) => [
        ...prev,
        {
          event: 'agent:error',
          status: 'error',
          message: `Network error: ${err.message}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsRunning(false);
    }
  };

  // Apply pending patch
  const handleApplyPatch = async () => {
    if (isApplying) return;
    setIsApplying(true);

    try {
      const res = await api.post('/schema/patch/apply', { business_id: businessId });
      const data = res.data;
      if (data.success) {
        setThoughtLogs((prev) => [
          ...prev,
          {
            event: 'agent:deployment_completed',
            status: 'success',
            message: `Patch applied! Website updated to v${data.new_version}. Same URL preserved.`,
            timestamp: new Date().toISOString(),
          },
        ]);
        setProposal(null);
        fetchHistory();
      } else {
        setThoughtLogs((prev) => [
          ...prev,
          {
            event: 'agent:error',
            status: 'error',
            message: data.error || 'Failed to apply patch.',
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (err) {
      console.error('Apply patch error:', err);
    } finally {
      setIsApplying(false);
    }
  };

  // Rollback
  const handleRollback = async () => {
    if (isRollingBack) return;
    setIsRollingBack(true);

    try {
      const res = await api.post('/schema/rollback', { business_id: businessId });
      const data = res.data;
      if (data.success) {
        setThoughtLogs((prev) => [
          ...prev,
          {
            event: 'agent:deployment_completed',
            status: 'success',
            message: `Rolled back to v${data.restored_version} successfully!`,
            timestamp: new Date().toISOString(),
          },
        ]);
        setProposal(null);
        fetchHistory();
      }
    } catch (err) {
      console.error('Rollback error:', err);
    } finally {
      setIsRollingBack(false);
    }
  };

  // Open drawer + fetch history
  const toggleDrawer = () => {
    const newState = !isOpen;
    setIsOpen(newState);
    if (newState) {
      fetchHistory();
    }
  };

  return (
    <>
      {/* Floating Trigger Button */}
      <button
        id="copilot-trigger-btn"
        className="copilot-trigger"
        onClick={toggleDrawer}
        title="AI Copilot"
      >
        <span className="copilot-trigger-icon">
          {isOpen ? '✕' : '🤖'}
        </span>
        {!isOpen && <span className="copilot-trigger-pulse" />}
      </button>

      {/* Backdrop */}
      {isOpen && <div className="copilot-backdrop" onClick={toggleDrawer} />}

      {/* Drawer Panel */}
      <div className={`copilot-drawer ${isOpen ? 'copilot-drawer--open' : ''}`}>
        {/* Header */}
        <div className="copilot-header">
          <div className="copilot-header-content">
            <div className="copilot-header-icon">🧠</div>
            <div>
              <h2 className="copilot-title">AI Business Copilot</h2>
              <p className="copilot-subtitle">Self-Improving Optimization Engine</p>
            </div>
          </div>
          <button className="copilot-close" onClick={toggleDrawer}>✕</button>
        </div>

        {/* Tab Navigation */}
        <div className="copilot-tabs">
          {['thoughts', 'proposal', 'timeline'].map((tab) => (
            <button
              key={tab}
              className={`copilot-tab ${activeTab === tab ? 'copilot-tab--active' : ''}`}
              onClick={() => {
                setActiveTab(tab);
                if (tab === 'timeline') fetchHistory();
              }}
            >
              {tab === 'thoughts' && '💭 Thoughts'}
              {tab === 'proposal' && '📋 Proposal'}
              {tab === 'timeline' && '📅 Timeline'}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="copilot-content">

          {/* THOUGHTS TAB */}
          {activeTab === 'thoughts' && (
            <div className="copilot-thoughts">
              {thoughtLogs.length === 0 && !isRunning && (
                <div className="copilot-empty">
                  <span className="copilot-empty-icon">🧬</span>
                  <p>Send a command to start the reflective optimization loop.</p>
                </div>
              )}
              {thoughtLogs.map((log, idx) => (
                <div
                  key={idx}
                  className={`thought-entry thought-entry--${log.status}`}
                >
                  <div className="thought-icon">
                    {STEP_ICONS[log.event] || '🔵'}
                  </div>
                  <div className="thought-body">
                    <div className="thought-label">
                      {STEP_LABELS[log.event] || log.event}
                    </div>
                    <div className="thought-message">{log.message}</div>
                    <div className="thought-time">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              {isRunning && (
                <div className="thought-entry thought-entry--active">
                  <div className="thought-icon thought-spinner">⚙️</div>
                  <div className="thought-body">
                    <div className="thought-label">Processing...</div>
                    <div className="thought-message">Agent is thinking...</div>
                  </div>
                </div>
              )}
              <div ref={logsEndRef} />
            </div>
          )}

          {/* PROPOSAL TAB */}
          {activeTab === 'proposal' && (
            <div className="copilot-proposal">
              {!proposal ? (
                <div className="copilot-empty">
                  <span className="copilot-empty-icon">📋</span>
                  <p>No active proposal. Run optimization first.</p>
                </div>
              ) : (
                <>
                  {/* Impact Card */}
                  <div className="impact-card">
                    <div className="impact-card-header">Expected Impact</div>
                    <div className="impact-card-body">
                      <div className="impact-metric">
                        <span className="impact-value">{proposal.expected_impact}</span>
                        <span className="impact-label">Conversion Boost</span>
                      </div>
                      <div className="impact-metric">
                        <span className="impact-value">{proposal.confidence}%</span>
                        <span className="impact-label">Confidence</span>
                      </div>
                    </div>
                  </div>

                  {/* Hypothesis */}
                  <div className="proposal-section">
                    <h4 className="proposal-section-title">💡 Hypothesis</h4>
                    <p className="proposal-text">
                      {proposal.hypothesis?.explanation || proposal.explanation}
                    </p>
                  </div>

                  {/* Delta View */}
                  {proposal.delta && (
                    <div className="proposal-section">
                      <h4 className="proposal-section-title">📐 Patch Delta</h4>
                      <div className="delta-view">
                        {proposal.delta.before && (
                          <div className="delta-panel delta-panel--before">
                            <div className="delta-label">Before</div>
                            <div className="delta-content">
                              <div className="delta-field">
                                <span className="delta-key">Variant:</span>
                                <span>{proposal.delta.before.variant}</span>
                              </div>
                              {proposal.delta.before.content?.title && (
                                <div className="delta-field">
                                  <span className="delta-key">Title:</span>
                                  <span>{proposal.delta.before.content.title}</span>
                                </div>
                              )}
                              {proposal.delta.before.content?.cta && (
                                <div className="delta-field">
                                  <span className="delta-key">CTA:</span>
                                  <span>{proposal.delta.before.content.cta}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                        {proposal.delta.after && (
                          <div className="delta-panel delta-panel--after">
                            <div className="delta-label">After</div>
                            <div className="delta-content">
                              <div className="delta-field">
                                <span className="delta-key">Variant:</span>
                                <span className="delta-changed">{proposal.delta.after.variant}</span>
                              </div>
                              {proposal.delta.after.content?.title && (
                                <div className="delta-field">
                                  <span className="delta-key">Title:</span>
                                  <span className="delta-changed">{proposal.delta.after.content.title}</span>
                                </div>
                              )}
                              {proposal.delta.after.content?.cta && (
                                <div className="delta-field">
                                  <span className="delta-key">CTA:</span>
                                  <span className="delta-changed">{proposal.delta.after.content.cta}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="proposal-actions">
                    <button
                      className="btn-apply"
                      onClick={handleApplyPatch}
                      disabled={isApplying}
                    >
                      {isApplying ? (
                        <><span className="btn-spinner" /> Applying...</>
                      ) : (
                        '✅ Apply Patch'
                      )}
                    </button>
                    <button
                      className="btn-rollback"
                      onClick={handleRollback}
                      disabled={isRollingBack}
                    >
                      {isRollingBack ? 'Rolling back...' : '⏪ Rollback'}
                    </button>
                  </div>
                </>
              )}
            </div>
          )}

          {/* TIMELINE TAB */}
          {activeTab === 'timeline' && (
            <div className="copilot-timeline">
              {versionHistory.length === 0 ? (
                <div className="copilot-empty">
                  <span className="copilot-empty-icon">📅</span>
                  <p>No version history yet.</p>
                </div>
              ) : (
                <div className="timeline-list">
                  {versionHistory.map((entry, idx) => (
                    <div key={idx} className="timeline-entry">
                      <div className="timeline-dot" />
                      <div className="timeline-body">
                        <div className="timeline-version">
                          v{entry.schema_version || entry.version}
                        </div>
                        <div className="timeline-meta">
                          {entry.patch_metadata?.patch_name || 'Schema update'}
                        </div>
                        <div className="timeline-reason">
                          {entry.patch_metadata?.trigger_reason || ''}
                        </div>
                        <div className="timeline-impact">
                          {entry.patch_metadata?.expected_impact || ''}
                          {entry.patch_metadata?.confidence_score && (
                            <span className="timeline-confidence">
                              &nbsp;· {entry.patch_metadata.confidence_score}% confidence
                            </span>
                          )}
                        </div>
                        <div className="timeline-time">
                          {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : ''}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Command Input */}
        <div className="copilot-input-area">
          <input
            id="copilot-command-input"
            type="text"
            className="copilot-input"
            placeholder="e.g. Move booking CTA above fold..."
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleOptimize()}
            disabled={isRunning}
          />
          <button
            id="copilot-run-btn"
            className="copilot-send"
            onClick={handleOptimize}
            disabled={isRunning || !command.trim()}
          >
            {isRunning ? '⏳' : '🚀'}
          </button>
        </div>
      </div>
    </>
  );
}
