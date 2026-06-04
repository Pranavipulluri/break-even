import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Sliders, Eye, History, RefreshCw, Check, ChevronDown, Undo2 } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const VARIANT_OPTIONS = [
  'hero-split', 'hero-centered', 'hero-fullwidth',
  'hero-minimal', 'hero-video', 'hero-gradient',
];

const THEME_PALETTES = [
  { id: 'ocean-blue', label: 'Ocean Blue', from: '#1e40af', to: '#3b82f6' },
  { id: 'rose-gold-luxury', label: 'Rose Gold', from: '#be185d', to: '#f472b6' },
  { id: 'emerald-nature', label: 'Emerald', from: '#065f46', to: '#34d399' },
  { id: 'sunset-warm', label: 'Sunset', from: '#c2410c', to: '#fb923c' },
  { id: 'slate-corporate', label: 'Slate', from: '#334155', to: '#94a3b8' },
  { id: 'violet-creative', label: 'Violet', from: '#6d28d9', to: '#a78bfa' },
];

export default function WebsiteSchemaLiveEditor() {
  const { user } = useAuth();
  const businessId = user?._id || user?.id || '';

  const [schema, setSchema] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingFields, setSavingFields] = useState({});
  const [historyOpen, setHistoryOpen] = useState(false);
  const [rollingBack, setRollingBack] = useState(false);

  const saving = Object.values(savingFields).some(Boolean);

  // Keep a ref of the absolute latest schema state to ensure up-to-date checks inside sequential queue
  const schemaRef = useRef(schema);
  useEffect(() => {
    schemaRef.current = schema;
  }, [schema]);

  // Sequential patch queue to prevent parallel patches from firing on concurrent blurs
  const patchQueueRef = useRef(Promise.resolve());

  // Editable fields — controlled state
  const [heroTitle, setHeroTitle] = useState('');
  const [heroSubtitle, setHeroSubtitle] = useState('');
  const [heroCta, setHeroCta] = useState('');
  const [heroVariant, setHeroVariant] = useState('');
  const [themePalette, setThemePalette] = useState('');

  // Load schema
  const fetchSchema = useCallback(async () => {
    if (!businessId) return;
    try {
      setLoading(true);
      const res = await api.get(`/schema/current/${businessId}`);
      if (res.data.success) {
        const s = res.data.schema;
        setSchema(s);
        // Populate editable fields from active schema
        const hero = (s.sections || []).find((sec) => sec.id?.startsWith('hero'));
        if (hero) {
          setHeroTitle(hero.content?.title || '');
          setHeroSubtitle(hero.content?.subtitle || '');
          setHeroCta(hero.content?.cta || '');
          setHeroVariant(hero.variant || '');
        }
        setThemePalette(s.theme?.palette || '');
      }
    } catch (err) {
      if (err.response?.status !== 404) {
        toast.error('Failed to load schema');
      }
    } finally {
      setLoading(false);
    }
  }, [businessId]);

  // Load history
  const fetchHistory = useCallback(async () => {
    if (!businessId) return;
    try {
      const res = await api.get(`/schema/history/${businessId}`);
      if (res.data.success) {
        setHistory(res.data.history || []);
      }
    } catch {
      // silently ignore
    }
  }, [businessId]);

  useEffect(() => {
    fetchSchema();
    fetchHistory();
  }, [fetchSchema, fetchHistory]);

  // Unified helper to apply a queued, direct patch
  const queueDirectPatch = (field, checkFn, patchFn) => {
    setSavingFields((prev) => ({ ...prev, [field]: true }));
    patchQueueRef.current = patchQueueRef.current.then(async () => {
      try {
        const currentSchema = schemaRef.current;
        if (!currentSchema) return;

        // Perform validation against the absolute latest schema in the queue
        if (!checkFn(currentSchema)) {
          return; // No actual change, skip patch
        }

        const { patch, reason } = patchFn(currentSchema);

        const res = await api.post('/schema/patch/apply', {
          business_id: businessId,
          patch,
          reason,
        });

        if (res.data.success) {
          toast.success(`Updated — v${res.data.new_version}`);
          await fetchSchema();
          await fetchHistory();
        } else {
          toast.error(res.data.error || 'Patch rejected');
        }
      } catch (err) {
        toast.error(err.response?.data?.error || 'Patch failed');
      } finally {
        setSavingFields((prev) => ({ ...prev, [field]: false }));
      }
    });
  };

  // Field-level save handlers — called on blur
  const saveHeroContent = (field, value) => {
    queueDirectPatch(
      field,
      (currentSchema) => {
        const heroSection = (currentSchema?.sections || []).find((s) => s.id?.startsWith('hero'));
        return heroSection && heroSection.content?.[field] !== value;
      },
      (currentSchema) => {
        const heroSection = (currentSchema?.sections || []).find((s) => s.id?.startsWith('hero'));
        return {
          patch: {
            action: 'update_section',
            section_id: heroSection.id,
            changes: { content: { [field]: value } },
          },
          reason: `Live edit: updated hero ${field}`,
        };
      }
    );
  };

  const saveVariant = (variant) => {
    setHeroVariant(variant);

    queueDirectPatch(
      'variant',
      (currentSchema) => {
        const heroSection = (currentSchema?.sections || []).find((s) => s.id?.startsWith('hero'));
        return heroSection && heroSection.variant !== variant;
      },
      (currentSchema) => {
        const heroSection = (currentSchema?.sections || []).find((s) => s.id?.startsWith('hero'));
        return {
          patch: {
            action: 'swap_variant',
            section_id: heroSection.id,
            variant,
          },
          reason: `Live edit: swapped hero variant to ${variant}`,
        };
      }
    );
  };

  const saveTheme = (palette) => {
    setThemePalette(palette);

    queueDirectPatch(
      'theme',
      (currentSchema) => {
        return currentSchema?.theme?.palette !== palette;
      },
      (currentSchema) => {
        return {
          patch: {
            action: 'update_theme',
            changes: { palette },
          },
          reason: `Live edit: changed theme palette to ${palette}`,
        };
      }
    );
  };

  // Rollback to a specific version
  const handleRollback = async (version) => {
    if (rollingBack) return;
    setRollingBack(true);
    try {
      const res = await api.post('/schema/rollback', {
        business_id: businessId,
        target_version: version,
      });
      if (res.data.success) {
        toast.success(`Rolled back to v${res.data.restored_version}`);
        await fetchSchema();
        await fetchHistory();
      }
    } catch (err) {
      toast.error('Rollback failed');
    } finally {
      setRollingBack(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="h-10 w-64 skeleton rounded-xl mb-4" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card"><div className="space-y-4">{[...Array(5)].map((_, i) => <div key={i} className="h-12 skeleton rounded-xl" />)}</div></div>
          <div className="card"><div className="h-80 skeleton rounded-xl" /></div>
        </div>
      </div>
    );
  }

  if (!schema) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center mb-6">
          <Sliders size={36} className="text-white" />
        </div>
        <h2 className="heading-3 mb-2">No Website Schema Found</h2>
        <p className="text-gray-500 max-w-md">
          Generate a website first using the Website Builder, then come back here to fine-tune
          your layout, copy, and theme in real time.
        </p>
      </div>
    );
  }

  const heroSection = (schema.sections || []).find((s) => s.id?.startsWith('hero'));

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="heading-1">Schema Live Editor</h1>
          <p className="text-gray-600 mt-2">
            Edit your website layout properties in real time — every change patches the live schema instantly.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="badge-primary">v{schema.schema_version || schema.version || 1}</span>
          <button onClick={() => { fetchSchema(); fetchHistory(); }} className="btn-secondary" disabled={saving}>
            <RefreshCw size={16} className={saving ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Dual Pane Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* LEFT: Form */}
        <div className="space-y-6">
          {/* Hero Content */}
          <div className="card-hover">
            <h3 className="heading-3 mb-6 flex items-center gap-2">
              <Sliders size={20} className="text-amber-500" /> Hero Section
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Hero Title</label>
                <input
                  id="editor-hero-title"
                  type="text"
                  className="input-field"
                  value={heroTitle}
                  onChange={(e) => setHeroTitle(e.target.value)}
                  onBlur={() => saveHeroContent('title', heroTitle)}
                  placeholder="Your hero headline..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Subtitle</label>
                <input
                  id="editor-hero-subtitle"
                  type="text"
                  className="input-field"
                  value={heroSubtitle}
                  onChange={(e) => setHeroSubtitle(e.target.value)}
                  onBlur={() => saveHeroContent('subtitle', heroSubtitle)}
                  placeholder="Supporting tagline..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">CTA Button Text</label>
                <input
                  id="editor-hero-cta"
                  type="text"
                  className="input-field"
                  value={heroCta}
                  onChange={(e) => setHeroCta(e.target.value)}
                  onBlur={() => saveHeroContent('cta', heroCta)}
                  placeholder="Call to action..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Layout Variant</label>
                <div className="grid grid-cols-2 gap-2">
                  {VARIANT_OPTIONS.map((v) => (
                    <button
                      key={v}
                      id={`editor-variant-${v}`}
                      onClick={() => saveVariant(v)}
                      className={`px-3 py-2 rounded-xl text-sm font-medium border transition-all duration-200 ${
                        heroVariant === v
                          ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white border-transparent shadow-lg'
                          : 'bg-white text-gray-600 border-gray-200 hover:border-amber-300 hover:text-amber-700'
                      }`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Theme Palette */}
          <div className="card-hover">
            <h3 className="heading-3 mb-6 flex items-center gap-2">
              <Eye size={20} className="text-violet-500" /> Theme Palette
            </h3>

            <div className="grid grid-cols-3 gap-3">
              {THEME_PALETTES.map((p) => (
                <button
                  key={p.id}
                  id={`editor-theme-${p.id}`}
                  onClick={() => saveTheme(p.id)}
                  className={`relative rounded-xl p-3 border transition-all duration-200 text-center ${
                    themePalette === p.id
                      ? 'border-2 border-violet-500 shadow-lg ring-2 ring-violet-200'
                      : 'border-gray-200 hover:border-violet-300'
                  }`}
                >
                  <div
                    className="w-full h-8 rounded-lg mb-2"
                    style={{ background: `linear-gradient(135deg, ${p.from}, ${p.to})` }}
                  />
                  <span className="text-xs font-medium text-gray-700">{p.label}</span>
                  {themePalette === p.id && (
                    <div className="absolute top-1 right-1 w-5 h-5 bg-violet-500 rounded-full flex items-center justify-center">
                      <Check size={12} className="text-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Saving Indicator */}
          {saving && (
            <div className="flex items-center gap-2 text-sm text-amber-600 font-medium animate-pulse">
              <RefreshCw size={14} className="animate-spin" />
              Patching schema...
            </div>
          )}
        </div>

        {/* RIGHT: Preview Panel */}
        <div className="space-y-6">
          <div className="card-hover">
            <h3 className="heading-3 mb-6 flex items-center gap-2">
              <Eye size={20} className="text-blue-500" /> Live Preview
            </h3>

            {/* Schema summary cards */}
            <div className="space-y-4">
              {/* Hero preview card */}
              {heroSection && (
                <div className="rounded-xl overflow-hidden border border-gray-100">
                  <div
                    className="p-6"
                    style={{
                      background: (() => {
                        const palette = THEME_PALETTES.find((p) => p.id === themePalette);
                        return palette
                          ? `linear-gradient(135deg, ${palette.from}, ${palette.to})`
                          : 'linear-gradient(135deg, #3b82f6, #6366f1)';
                      })(),
                    }}
                  >
                    <div className="text-white">
                      <p className="text-xs font-semibold uppercase tracking-widest opacity-70 mb-2">
                        {heroVariant || 'hero-split'}
                      </p>
                      <h2 className="text-xl font-bold mb-2">{heroTitle || 'Your Headline'}</h2>
                      <p className="text-sm opacity-80 mb-4">{heroSubtitle || 'Supporting subtitle text'}</p>
                      <div className="inline-block px-4 py-2 bg-white/20 backdrop-blur rounded-lg text-sm font-semibold">
                        {heroCta || 'Call to Action'}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Section list */}
              <div>
                <h4 className="text-sm font-semibold text-gray-600 mb-3">All Sections</h4>
                <div className="space-y-2">
                  {(schema.sections || []).map((section, idx) => (
                    <div
                      key={section.id || idx}
                      className="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-xl border border-gray-100"
                    >
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-500 text-white text-xs rounded-lg flex items-center justify-center font-bold">
                          {idx + 1}
                        </span>
                        <div>
                          <p className="text-sm font-semibold text-gray-800">{section.id}</p>
                          <p className="text-xs text-gray-500">{section.type} · {section.variant || 'default'}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Schema metadata */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 rounded-xl text-center">
                  <p className="text-2xl font-bold text-blue-700">{(schema.sections || []).length}</p>
                  <p className="text-xs text-blue-500 font-medium">Sections</p>
                </div>
                <div className="p-4 bg-violet-50 rounded-xl text-center">
                  <p className="text-2xl font-bold text-violet-700">v{schema.schema_version || schema.version || 1}</p>
                  <p className="text-xs text-violet-500 font-medium">Version</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom: Version History Timeline */}
      <div className="card-hover">
        <button
          onClick={() => { setHistoryOpen(!historyOpen); if (!historyOpen) fetchHistory(); }}
          className="w-full flex items-center justify-between"
        >
          <h3 className="heading-3 flex items-center gap-2">
            <History size={20} className="text-emerald-500" /> Version Timeline
            <span className="badge-ghost ml-2">{history.length}</span>
          </h3>
          <ChevronDown size={20} className={`text-gray-400 transition-transform duration-200 ${historyOpen ? 'rotate-180' : ''}`} />
        </button>

        {historyOpen && (
          <div className="mt-6 relative">
            {history.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">No version history yet.</p>
            ) : (
              <div className="space-y-0 pl-6 border-l-2 border-gray-200">
                {history.map((entry, idx) => (
                  <div key={idx} className="relative pb-6 last:pb-0 group">
                    {/* Dot */}
                    <div className="absolute -left-[25px] top-1 w-3 h-3 rounded-full bg-emerald-400 border-2 border-white shadow group-hover:scale-125 transition-transform" />

                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-sm font-bold text-gray-900">
                          v{entry.schema_version || entry.version}
                        </p>
                        <p className="text-xs text-emerald-600 font-medium">
                          {entry.patch_metadata?.patch_name || 'Schema update'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {entry.patch_metadata?.trigger_reason || ''}
                        </p>
                        {entry.patch_metadata?.expected_impact && (
                          <p className="text-xs font-semibold text-emerald-500 mt-1">
                            {entry.patch_metadata.expected_impact}
                            {entry.patch_metadata?.confidence_score && (
                              <span className="text-gray-400 font-normal ml-1">
                                · {entry.patch_metadata.confidence_score}% confidence
                              </span>
                            )}
                          </p>
                        )}
                        <p className="text-xs text-gray-400 mt-1">
                          {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : ''}
                        </p>
                      </div>

                      <button
                        onClick={() => {
                          const targetVersion = entry.schema_version || entry.version;
                          if (window.confirm(`Are you sure you want to restore and roll back your live website to version v${targetVersion}?`)) {
                            handleRollback(targetVersion);
                          }
                        }}
                        disabled={rollingBack}
                        className="opacity-0 group-hover:opacity-100 transition-opacity btn-sm btn-secondary flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
                        title={`Rollback to v${entry.schema_version || entry.version}`}
                      >
                        <Undo2 size={12} />
                        Restore
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
