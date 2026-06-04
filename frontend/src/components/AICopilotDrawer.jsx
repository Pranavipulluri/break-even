import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import webSocketService from '../services/websocket';
import './AICopilotDrawer.css';

const STEP_ICONS = {
  'agent:observe': '🔍',
  'agent:analyze': '📊',
  'agent:hypothesis': '💡',
  'agent:failure_gate': '🛡️',
  'agent:patch_generated': '🧬',
  'agent:validation_passed': '✅',
  'agent:awaiting_approval': '⏳',
  'agent:deployment_started': '🚀',
  'agent:deployment_completed': '🎉',
  'agent:error': '❌',
};

const STEP_LABELS = {
  'agent:observe': 'Observing',
  'agent:analyze': 'Retrieving RAG Memory',
  'agent:hypothesis': 'Hypothesizing',
  'agent:failure_gate': 'Failure Gate',
  'agent:patch_generated': 'Patch Generated',
  'agent:validation_passed': 'Sandbox Validated',
  'agent:awaiting_approval': 'Awaiting Approval',
  'agent:deployment_started': 'Deploying',
  'agent:deployment_completed': 'Deployed',
  'agent:error': 'Error',
};

export default function AICopilotDrawer({ businessId }) {
  const { user } = useAuth();
  const { engagementMetrics, dispatch } = useApp();

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

  const resolvedId = businessId || user?._id || user?.id || '';

  // Fallback: Fetch engagement metrics if null and drawer is opened
  useEffect(() => {
    const fetchMetrics = async () => {
      if (isOpen && !engagementMetrics && resolvedId) {
        try {
          const res = await api.get(`/events/summary/${resolvedId}?days=30`);
          if (res.data?.success) {
            const summary = res.data.summary;
            dispatch({
              type: 'SET_ENGAGEMENT_METRICS',
              payload: {
                bounce_rate: summary.bounce_rate || 0,
                cta_click_rate: summary.cta_click_rate || 0,
                booking_conversion_rate: summary.booking_conversion_rate || 0,
                page_views: summary.page_view || 0,
                cta_clicks: summary.cta_click || 0,
                bounces: summary.bounce || 0,
              },
            });
          }
        } catch (err) {
          console.error('Failed to fetch engagement metrics in drawer fallback:', err);
        }
      }
    };
    fetchMetrics();
  }, [isOpen, engagementMetrics, resolvedId, dispatch]);

  // Pre-fill command with engagement context when drawer opens
  useEffect(() => {
    if (isOpen && engagementMetrics && !command) {
      const bounce = engagementMetrics.bounce_rate ?? 'N/A';
      const conversion = engagementMetrics.booking_conversion_rate ?? 'N/A';
      setCommand(
        `Optimize my website. Current bounce rate: ${bounce}%, booking conversion: ${conversion}%`
      );
    }
  }, [isOpen, engagementMetrics, command]);

  // Connect to shared Socket.IO for live thought streaming
  useEffect(() => {
    if (!resolvedId) return;

    webSocketService.connect(resolvedId);
    webSocketService.emit('join_agent_room', { business_id: resolvedId });

    const handleThoughtLog = (log) => {
      setThoughtLogs((prev) => [...prev, log]);
    };

    webSocketService.on('agent_thought_log', handleThoughtLog);

    return () => {
      webSocketService.off('agent_thought_log', handleThoughtLog);
    };
  }, [resolvedId]);

  // Auto-scroll thought logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [thoughtLogs]);

  // Fetch version history
  const fetchHistory = useCallback(async () => {
    if (!resolvedId) return;
    try {
      const res = await api.get(`/schema/history/${resolvedId}`);
      if (res.data.success) {
        setVersionHistory(res.data.history || []);
      }
    } catch (err) {
      console.error('Failed to fetch version history:', err);
    }
  }, [resolvedId]);

  // Abort controller for cancellation
  const abortRef = useRef(null);

  // Run optimization loop
  const handleOptimize = async () => {
    if (!command.trim() || isRunning) return;

    setIsRunning(true);
    setThoughtLogs([]);
    setProposal(null);
    setActiveTab('thoughts');

    // Create abort controller for cancellation
    const controller = new AbortController();
    abortRef.current = controller;

    // 60-second timeout
    const timeoutId = setTimeout(() => {
      controller.abort();
      setThoughtLogs((prev) => [
        ...prev,
        {
          event: 'agent:error',
          status: 'error',
          message: 'Optimization timed out after 60 seconds. The backend may be overloaded — please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
      setIsRunning(false);
    }, 60000);

    try {
      const res = await api.post('/agents/optimize', {
        command: command.trim(),
        business_id: resolvedId,
      }, { signal: controller.signal });

      clearTimeout(timeoutId);
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
      clearTimeout(timeoutId);
      if (err.name === 'AbortError' || err.name === 'CanceledError') {
        // Already handled by timeout or manual cancel
        return;
      }
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
      abortRef.current = null;
    }
  };

  // Cancel a running optimization
  const handleCancelOptimize = () => {
    if (abortRef.current) {
      abortRef.current.abort();
      setThoughtLogs((prev) => [
        ...prev,
        {
          event: 'agent:error',
          status: 'cancelled',
          message: 'Optimization cancelled by user.',
          timestamp: new Date().toISOString(),
        },
      ]);
      setIsRunning(false);
      abortRef.current = null;
    }
  };

  // Apply pending patch
  const handleApplyPatch = async () => {
    if (isApplying) return;
    setIsApplying(true);

    try {
      const res = await api.post('/schema/patch/apply', { business_id: resolvedId });
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

  // Rollback to a specific version
  const handleRollback = async (targetVersion = null) => {
    if (isRollingBack) return;
    setIsRollingBack(true);

    try {
      const payload = { business_id: resolvedId };
      if (targetVersion !== null) payload.target_version = targetVersion;

      const res = await api.post('/schema/rollback', payload);
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
    } else {
      setCommand('');
    }
  };

  // Render a single delta field row
  const DeltaField = ({ label, before, after }) => {
    const changed = before !== after;
    return (
      <div className="delta-field">
        <span className="delta-key">{label}:</span>
        <span className={changed ? 'delta-changed' : ''}>{after || '—'}</span>
      </div>
    );
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
                  <p style={{ marginTop: 8, fontSize: 11, color: 'var(--copilot-text-muted)' }}>
                    Observe → Retrieve → Failure Gate → Hypothesis → Patch → Validate → Impact
                  </p>
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
                    <button
                      className="copilot-cancel-btn"
                      onClick={handleCancelOptimize}
                      style={{
                        marginTop: 8,
                        padding: '4px 12px',
                        fontSize: 11,
                        background: 'rgba(239,68,68,0.15)',
                        color: '#ef4444',
                        border: '1px solid rgba(239,68,68,0.3)',
                        borderRadius: 6,
                        cursor: 'pointer',
                      }}
                    >
                      ✕ Cancel
                    </button>
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

                  {/* Failure Gate Summary */}
                  {proposal.failure_gate_result && proposal.failure_gate_result.matches_found > 0 && (
                    <div className="proposal-section" style={{ borderLeft: '3px solid var(--copilot-warning)' }}>
                      <h4 className="proposal-section-title">⚠️ Failure Gate</h4>
                      <p className="proposal-text" style={{ color: 'var(--copilot-warning)' }}>
                        {proposal.failure_gate_result.matches_found} similar past failure(s) detected.
                        Hypothesis was adjusted to avoid repeating them.
                      </p>
                    </div>
                  )}

                  {/* Side-by-Side Delta View */}
                  {proposal.delta && (
                    <div className="proposal-section">
                      <h4 className="proposal-section-title">📐 Before / After Delta</h4>
                      <div className="delta-view" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                        {/* BEFORE Panel */}
                        <div className="delta-panel delta-panel--before">
                          <div className="delta-label">Before</div>
                          <div className="delta-content">
                            {proposal.delta.before?.variant && (
                              <DeltaField
                                label="Variant"
                                before={proposal.delta.before.variant}
                                after={proposal.delta.before.variant}
                              />
                            )}
                            {proposal.delta.before?.content?.title && (
                              <DeltaField
                                label="Title"
                                before={proposal.delta.before.content.title}
                                after={proposal.delta.before.content.title}
                              />
                            )}
                            {proposal.delta.before?.content?.cta && (
                              <DeltaField
                                label="CTA"
                                before={proposal.delta.before.content.cta}
                                after={proposal.delta.before.content.cta}
                              />
                            )}
                            {proposal.delta.before?.content?.subtitle && (
                              <DeltaField
                                label="Subtitle"
                                before={proposal.delta.before.content.subtitle}
                                after={proposal.delta.before.content.subtitle}
                              />
                            )}
                          </div>
                        </div>

                        {/* AFTER Panel */}
                        <div className="delta-panel delta-panel--after">
                          <div className="delta-label">After</div>
                          <div className="delta-content">
                            {(proposal.delta.after?.variant || proposal.delta.before?.variant) && (
                              <DeltaField
                                label="Variant"
                                before={proposal.delta.before?.variant}
                                after={proposal.delta.after?.variant}
                              />
                            )}
                            {(proposal.delta.after?.content?.title || proposal.delta.before?.content?.title) && (
                              <DeltaField
                                label="Title"
                                before={proposal.delta.before?.content?.title}
                                after={proposal.delta.after?.content?.title}
                              />
                            )}
                            {(proposal.delta.after?.content?.cta || proposal.delta.before?.content?.cta) && (
                              <DeltaField
                                label="CTA"
                                before={proposal.delta.before?.content?.cta}
                                after={proposal.delta.after?.content?.cta}
                              />
                            )}
                            {(proposal.delta.after?.content?.subtitle || proposal.delta.before?.content?.subtitle) && (
                              <DeltaField
                                label="Subtitle"
                                before={proposal.delta.before?.content?.subtitle}
                                after={proposal.delta.after?.content?.subtitle}
                              />
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Reorder delta */}
                      {proposal.delta.before_order && (
                        <div style={{ marginTop: 12 }}>
                          <div className="delta-field">
                            <span className="delta-key">Section order:</span>
                            <span className="delta-changed">
                              {proposal.delta.after_order?.join(' → ') || 'unchanged'}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Validation Report */}
                  {proposal.validation_report && (
                    <div className="proposal-section">
                      <h4 className="proposal-section-title">🛡️ Validation Report</h4>
                      <p className="proposal-text" style={{ color: 'var(--copilot-success)' }}>
                        ✓ {proposal.validation_report.checks_passed || 0} checks passed
                        {proposal.validation_report.warnings?.length > 0 && (
                          <span style={{ color: 'var(--copilot-warning)', marginLeft: 8 }}>
                            ⚠ {proposal.validation_report.warnings.length} advisory warning(s)
                          </span>
                        )}
                      </p>
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
                      onClick={() => {
                        if (window.confirm("Are you sure you want to roll back your website to the previous version?")) {
                          handleRollback();
                        }
                      }}
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
                    <div
                      key={idx}
                      className="timeline-entry"
                      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}
                    >
                      <div className="timeline-dot" style={{ marginTop: '8px' }} />
                      <div className="timeline-body" style={{ flex: 1 }}>
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

                      <button
                        onClick={() => {
                          const targetVer = entry.schema_version || entry.version;
                          if (window.confirm(`Are you sure you want to restore and roll back your live website to version v${targetVer}?`)) {
                            handleRollback(targetVer);
                          }
                        }}
                        disabled={isRollingBack}
                        className="btn-rollback"
                        style={{
                          padding: '6px 12px',
                          fontSize: '11px',
                          borderRadius: '8px',
                          height: 'fit-content',
                          whiteSpace: 'nowrap'
                        }}
                        title={`Rollback to v${entry.schema_version || entry.version}`}
                      >
                        Restore
                      </button>
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
