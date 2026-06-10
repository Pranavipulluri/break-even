import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Sliders, Eye, History, RefreshCw, Check, ChevronDown, Undo2, 
  Plus, Trash2, Sparkles, MessageSquare, Users, Calendar, 
  Phone, FileText, Megaphone, DollarSign, Layout 
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const THEME_PALETTES = [
  { id: 'royal-navy', label: 'Royal Navy', from: '#1d2a44', to: '#3b5998' },
  { id: 'rose-gold-luxury', label: 'Rose Gold', from: '#b76e79', to: '#e4b4b8' },
  { id: 'emerald-gold', label: 'Emerald Gold', from: '#044a27', to: '#d4af37' },
  { id: 'spa-serenity', label: 'Spa Serenity', from: '#8fa89b', to: '#d0dfd8' },
  { id: 'lavender-luxury', label: 'Lavender Luxury', from: '#a799b7', to: '#d6cbd9' },
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

  // Selected section state
  const [selectedSectionId, setSelectedSectionId] = useState('');
  const [activeTitle, setActiveTitle] = useState('');
  const [activeSubtitle, setActiveSubtitle] = useState('');
  const [activeCta, setActiveCta] = useState('');
  const [activeVariant, setActiveVariant] = useState('');
  const [activeAddress, setActiveAddress] = useState('');
  const [activePhone, setActivePhone] = useState('');
  const [activeEmail, setActiveEmail] = useState('');
  const [activeItems, setActiveItems] = useState([]);
  const [activeImage, setActiveImage] = useState('');
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

  // Sync initial selection
  useEffect(() => {
    if (schema && schema.sections && schema.sections.length > 0) {
      if (!selectedSectionId || !schema.sections.some(s => s.id === selectedSectionId)) {
        setSelectedSectionId(schema.sections[0].id);
      }
    }
  }, [schema, selectedSectionId]);

  // Sync active states on section change
  useEffect(() => {
    if (!schema || !selectedSectionId) return;
    const section = (schema.sections || []).find((s) => s.id === selectedSectionId);
    if (section) {
      setActiveTitle(section.content?.title || '');
      setActiveSubtitle(section.content?.subtitle || '');
      setActiveCta(section.content?.cta || '');
      setActiveVariant(section.variant || '');
      setActiveAddress(section.content?.address || '');
      setActivePhone(section.content?.phone || '');
      setActiveEmail(section.content?.email || '');
      setActiveImage(section.content?.image || '');
      if (section.type === 'booking') {
        setActiveItems(section.content?.services || []);
      } else {
        setActiveItems(section.content?.items || []);
      }
    }
  }, [selectedSectionId, schema]);

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

  // Generic content saving handler
  const saveSectionContent = (sectionId, field, value) => {
    queueDirectPatch(
      `${sectionId}-${field}`,
      (currentSchema) => {
        const section = (currentSchema?.sections || []).find((s) => s.id === sectionId);
        return section && JSON.stringify(section.content?.[field]) !== JSON.stringify(value);
      },
      (currentSchema) => {
        return {
          patch: {
            action: 'update_section',
            section_id: sectionId,
            changes: { content: { [field]: value } },
          },
          reason: `Live edit: updated ${sectionId} ${field}`,
        };
      }
    );
  };

  // Generic variant swapping handler
  const saveVariant = (sectionId, variant) => {
    setActiveVariant(variant);

    queueDirectPatch(
      `${sectionId}-variant`,
      (currentSchema) => {
        const section = (currentSchema?.sections || []).find((s) => s.id === sectionId);
        return section && section.variant !== variant;
      },
      (currentSchema) => {
        return {
          patch: {
            action: 'swap_variant',
            section_id: sectionId,
            variant,
          },
          reason: `Live edit: swapped ${sectionId} variant to ${variant}`,
        };
      }
    );
  };

  // Generic list items saving handler
  const saveSectionItems = (sectionId, items) => {
    queueDirectPatch(
      `${sectionId}-items`,
      (currentSchema) => {
        const section = (currentSchema?.sections || []).find((s) => s.id === sectionId);
        return section && JSON.stringify(section.content?.items) !== JSON.stringify(items);
      },
      (currentSchema) => {
        return {
          patch: {
            action: 'update_section',
            section_id: sectionId,
            changes: { content: { items } },
          },
          reason: `Live edit: updated ${sectionId} items`,
        };
      }
    );
  };

  // List item management functions
  const handleItemChange = (index, field, value) => {
    const updated = [...activeItems];
    updated[index] = { ...updated[index], [field]: value };
    setActiveItems(updated);
  };

  const handleItemBlur = () => {
    saveSectionItems(selectedSectionId, activeItems);
  };

  const addItem = () => {
    const newItem = {};
    const activeSection = (schema.sections || []).find((s) => s.id === selectedSectionId);
    if (!activeSection) return;

    if (activeSection.type === 'services') {
      newItem.name = 'New Service';
      newItem.description = 'Service description';
      newItem.price = '$0';
      newItem.icon = 'fas fa-star';
    } else if (activeSection.type === 'testimonials') {
      newItem.name = 'Client Name';
      newItem.role = 'Client';
      newItem.quote = 'Awesome experience!';
    } else if (activeSection.type === 'team') {
      newItem.name = 'Team Member';
      newItem.role = 'Specialist';
      newItem.bio = 'Bio description';
      newItem.photo = 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400';
    } else if (activeSection.type === 'pricing') {
      newItem.name = 'Plan Name';
      newItem.price = '$0';
      newItem.period = 'month';
      newItem.features = ['Feature 1'];
    }

    const updated = [...activeItems, newItem];
    setActiveItems(updated);
    saveSectionItems(selectedSectionId, updated);
  };

  const removeItem = (index) => {
    const updated = activeItems.filter((_, i) => i !== index);
    setActiveItems(updated);
    saveSectionItems(selectedSectionId, updated);
  };

  // Booking service management functions
  const handleBookingServiceChange = (index, value) => {
    const updated = [...activeItems];
    updated[index] = value;
    setActiveItems(updated);
  };

  const handleBookingServiceBlur = () => {
    saveSectionContent(selectedSectionId, 'services', activeItems);
  };

  const addBookingService = () => {
    const updated = [...activeItems, 'New Service Name'];
    setActiveItems(updated);
    saveSectionContent(selectedSectionId, 'services', updated);
  };

  const removeBookingService = (index) => {
    const updated = activeItems.filter((_, i) => i !== index);
    setActiveItems(updated);
    saveSectionContent(selectedSectionId, 'services', updated);
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

  const getDefaultSectionData = (type) => {
    const randomSuffix = Math.random().toString(36).substring(2, 7);
    const id = `${type}-${randomSuffix}`;
    let content = {};
    let variant = '';

    if (type === 'hero') {
      content = {
        title: 'Premium Title Built for You',
        subtitle: 'Add a professional description here outlining your core customer benefits.',
        cta: 'Book Appointment',
        image: 'https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=1200'
      };
      variant = 'hero-split';
    } else if (type === 'services') {
      content = {
        title: 'Our Premium Services',
        items: [
          { name: 'Standard Consultation', price: '$80', description: 'Focused session detailing your primary goals.', icon: 'fas fa-spa' },
          { name: 'Advanced Session', price: '$150', description: 'Comprehensive package detailing complete analysis.', icon: 'fas fa-gem' }
        ]
      };
      variant = 'services-grid';
    } else if (type === 'testimonials') {
      content = {
        title: 'Client Endorsements',
        items: [
          { name: 'Alice Smith', role: 'Business Owner', quote: 'Exceptional responsiveness and attention to detail.' }
        ]
      };
      variant = 'testimonials-grid';
    } else if (type === 'team') {
      content = {
        title: 'Meet the Team',
        members: [
          { name: 'Sarah Connor', role: 'Director', bio: 'Over 10 years experience.', photo: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400' }
        ]
      };
      variant = 'team-cards';
    } else if (type === 'booking') {
      content = {
        title: 'Book a Slot',
        business_id: businessId,
        services: ['Consultation', 'Premium Support']
      };
      variant = 'booking-embedded';
    } else if (type === 'contact') {
      content = {
        title: 'Get In Touch',
        business_id: businessId,
        address: '123 Main St, Suite 100',
        phone: '(555) 123-4567',
        email: 'info@business.com'
      };
      variant = 'contact-split';
    } else if (type === 'gallery') {
      content = {
        title: 'Our Visual Showcase',
        images: [
          { url: 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600', alt: 'Gallery Item 1' },
          { url: 'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600', alt: 'Gallery Item 2' }
        ]
      };
      variant = 'gallery-grid';
    } else if (type === 'pricing') {
      content = {
        title: 'Pricing & Plans',
        plans: [
          { name: 'Basic', price: '$49', period: '/mo', features: ['Consultation', 'Email access'], highlight: false },
          { name: 'Pro', price: '$99', period: '/mo', features: ['All Basic features', 'Priority booking', 'Dedicated therapist'], highlight: true }
        ]
      };
      variant = 'pricing-cards';
    } else if (type === 'cta') {
      content = {
        title: 'Start Your Journey Today',
        subtitle: 'Reserve your appointment slots now for the best treatment.',
        cta: 'Book Now'
      };
      variant = 'cta-banner';
    }

    return { id, type, variant, content };
  };

  const handleAddSection = (type) => {
    const sectionData = getDefaultSectionData(type);

    queueDirectPatch(
      `add-section-${sectionData.id}`,
      (currentSchema) => {
        return !(currentSchema?.sections || []).some((s) => s.id === sectionData.id);
      },
      (currentSchema) => {
        return {
          patch: {
            action: 'add_section',
            section_data: sectionData,
          },
          reason: `Live edit: added new ${type} section with ID ${sectionData.id}`,
        };
      }
    );
  };

  const handleDeleteSection = (sectionId) => {
    if (!window.confirm(`Are you sure you want to delete the entire "${sectionId}" section from your website?`)) {
      return;
    }
    queueDirectPatch(
      `delete-section-${sectionId}`,
      (currentSchema) => {
        return (currentSchema?.sections || []).some((s) => s.id === sectionId);
      },
      (currentSchema) => {
        return {
          patch: {
            action: 'delete_section',
            section_id: sectionId,
          },
          reason: `Live edit: deleted section ${sectionId}`,
        };
      }
    );
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

  const activeSection = (schema.sections || []).find((s) => s.id === selectedSectionId);

  const getSectionIcon = (type) => {
    switch (type) {
      case 'hero':
        return <Layout size={20} className="text-amber-500" />;
      case 'services':
        return <Sparkles size={20} className="text-blue-500" />;
      case 'testimonials':
        return <MessageSquare size={20} className="text-emerald-500" />;
      case 'team':
        return <Users size={20} className="text-indigo-500" />;
      case 'booking':
        return <Calendar size={20} className="text-violet-500" />;
      case 'contact':
        return <Phone size={20} className="text-pink-500" />;
      case 'cta':
        return <Megaphone size={20} className="text-red-500" />;
      case 'pricing':
        return <DollarSign size={20} className="text-cyan-500" />;
      default:
        return <FileText size={20} className="text-gray-500" />;
    }
  };

  const ALLOWED_VARIANTS = {
    hero: ['hero-split', 'hero-centered', 'hero-minimal', 'hero-luxury'],
    services: ['services-grid', 'services-list', 'services-carousel'],
    testimonials: ['testimonials-grid', 'testimonials-carousel'],
    team: ['team-cards', 'team-list'],
    booking: ['booking-embedded', 'booking-modal'],
    contact: ['contact-split', 'contact-centered'],
    footer: ['footer-standard', 'footer-minimal'],
    gallery: ['gallery-grid', 'gallery-masonry', 'gallery-carousel'],
    cta: ['cta-banner', 'cta-card', 'cta-floating'],
    pricing: ['pricing-cards', 'pricing-table', 'pricing-toggle'],
  };

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
        {/* LEFT: Dynamic Form Panel */}
        <div className="space-y-6">
          {activeSection && (
            <div className="card-hover">
              <h3 className="heading-3 mb-6 flex items-center gap-2 w-full">
                {getSectionIcon(activeSection.type)}
                <span className="capitalize">{activeSection.type} Section</span>
                <span className="text-xs font-normal text-gray-400 font-mono bg-gray-100 px-2 py-0.5 rounded">
                  {activeSection.id}
                </span>
                <button
                  onClick={() => handleDeleteSection(activeSection.id)}
                  className="ml-auto text-gray-400 hover:text-red-500 p-1.5 rounded-lg hover:bg-red-50 transition-all duration-200 flex items-center gap-1 text-xs font-semibold"
                  title="Delete Entire Section"
                >
                  <Trash2 size={14} /> Delete
                </button>
              </h3>

              <div className="space-y-4">
                {/* Section Title Input */}
                {activeSection.content && 'title' in activeSection.content && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">Section Title</label>
                    <input
                      type="text"
                      className="input-field"
                      value={activeTitle}
                      onChange={(e) => setActiveTitle(e.target.value)}
                      onBlur={() => saveSectionContent(selectedSectionId, 'title', activeTitle)}
                      placeholder="Enter title text..."
                    />
                  </div>
                )}

                {/* Section Subtitle Input */}
                {activeSection.content && 'subtitle' in activeSection.content && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">Subtitle / Description</label>
                    <input
                      type="text"
                      className="input-field"
                      value={activeSubtitle}
                      onChange={(e) => setActiveSubtitle(e.target.value)}
                      onBlur={() => saveSectionContent(selectedSectionId, 'subtitle', activeSubtitle)}
                      placeholder="Enter subtitle text..."
                    />
                  </div>
                )}

                {/* Section CTA Input */}
                {activeSection.content && 'cta' in activeSection.content && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">CTA Button Text</label>
                    <input
                      type="text"
                      className="input-field"
                      value={activeCta}
                      onChange={(e) => setActiveCta(e.target.value)}
                      onBlur={() => saveSectionContent(selectedSectionId, 'cta', activeCta)}
                      placeholder="Enter call to action text..."
                    />
                  </div>
                )}

                {/* Section Image Input */}
                {activeSection.content && 'image' in activeSection.content && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">Section / Background Image URL</label>
                    <input
                      type="text"
                      className="input-field"
                      value={activeImage}
                      onChange={(e) => setActiveImage(e.target.value)}
                      onBlur={() => saveSectionContent(selectedSectionId, 'image', activeImage)}
                      placeholder="Enter image URL..."
                    />
                  </div>
                )}

                {/* Contact specific inputs */}
                {activeSection.type === 'contact' && (
                  <>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-1.5">Address</label>
                      <input
                        type="text"
                        className="input-field"
                        value={activeAddress}
                        onChange={(e) => setActiveAddress(e.target.value)}
                        onBlur={() => saveSectionContent(selectedSectionId, 'address', activeAddress)}
                        placeholder="Physical address..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-1.5">Phone Number</label>
                      <input
                        type="text"
                        className="input-field"
                        value={activePhone}
                        onChange={(e) => setActivePhone(e.target.value)}
                        onBlur={() => saveSectionContent(selectedSectionId, 'phone', activePhone)}
                        placeholder="Contact phone..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-1.5">Email Address</label>
                      <input
                        type="email"
                        className="input-field"
                        value={activeEmail}
                        onChange={(e) => setActiveEmail(e.target.value)}
                        onBlur={() => saveSectionContent(selectedSectionId, 'email', activeEmail)}
                        placeholder="Contact email..."
                      />
                    </div>
                  </>
                )}

                {/* Section Layout Variant Picker */}
                {ALLOWED_VARIANTS[activeSection.type] && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">Layout Variant</label>
                    <div className="grid grid-cols-2 gap-2">
                      {ALLOWED_VARIANTS[activeSection.type].map((v) => (
                        <button
                          key={v}
                          onClick={() => saveVariant(selectedSectionId, v)}
                          className={`px-3 py-2 rounded-xl text-sm font-medium border transition-all duration-200 ${
                            activeVariant === v
                              ? 'bg-gradient-to-r from-violet-500 to-indigo-500 text-white border-transparent shadow-md font-bold'
                              : 'bg-white text-gray-600 border-gray-200 hover:border-violet-300 hover:text-violet-700'
                          }`}
                        >
                          {v}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* List Items Editor (services, testimonials, team, pricing) */}
                {['services', 'testimonials', 'team', 'pricing'].includes(activeSection.type) && (
                  <div className="space-y-4 border-t border-gray-100 pt-6 mt-6">
                    <div className="flex items-center justify-between">
                      <label className="block text-sm font-semibold text-gray-700">List Items ({activeItems.length})</label>
                      <button
                        onClick={addItem}
                        className="btn-sm btn-secondary flex items-center gap-1 text-xs py-1"
                      >
                        <Plus size={14} /> Add Item
                      </button>
                    </div>

                    <div className="space-y-4 max-h-[400px] overflow-y-auto pr-1">
                      {activeItems.map((item, idx) => (
                        <div key={idx} className="p-4 bg-gray-50 rounded-xl border border-gray-200 relative group space-y-3">
                          <button
                            onClick={() => removeItem(idx)}
                            className="absolute top-2 right-2 text-gray-400 hover:text-red-500 p-1 rounded-lg hover:bg-white transition-all duration-200"
                            title="Delete Item"
                          >
                            <Trash2 size={14} />
                          </button>

                          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Item #{idx + 1}</span>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {activeSection.type === 'services' && (
                              <>
                                <div className="md:col-span-2">
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Service Name</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.name || ''}
                                    onChange={(e) => handleItemChange(idx, 'name', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Price (optional)</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.price || ''}
                                    onChange={(e) => handleItemChange(idx, 'price', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Icon Class</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.icon || 'fas fa-star'}
                                    onChange={(e) => handleItemChange(idx, 'icon', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div className="md:col-span-2">
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Description</label>
                                  <textarea
                                    rows={2}
                                    className="input-field py-1 px-2 text-sm resize-none"
                                    value={item.description || ''}
                                    onChange={(e) => handleItemChange(idx, 'description', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                              </>
                            )}

                            {activeSection.type === 'testimonials' && (
                              <>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Author Name</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.name || ''}
                                    onChange={(e) => handleItemChange(idx, 'name', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Role / Company</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.role || ''}
                                    onChange={(e) => handleItemChange(idx, 'role', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div className="md:col-span-2">
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Quote</label>
                                  <textarea
                                    rows={2}
                                    className="input-field py-1 px-2 text-sm resize-none"
                                    value={item.quote || ''}
                                    onChange={(e) => handleItemChange(idx, 'quote', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                              </>
                            )}

                            {activeSection.type === 'team' && (
                              <>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Member Name</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.name || ''}
                                    onChange={(e) => handleItemChange(idx, 'name', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Role</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.role || ''}
                                    onChange={(e) => handleItemChange(idx, 'role', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div className="md:col-span-2">
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Photo URL</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.photo || ''}
                                    onChange={(e) => handleItemChange(idx, 'photo', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div className="md:col-span-2">
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Bio</label>
                                  <textarea
                                    rows={2}
                                    className="input-field py-1 px-2 text-sm resize-none"
                                    value={item.bio || ''}
                                    onChange={(e) => handleItemChange(idx, 'bio', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                              </>
                            )}

                            {activeSection.type === 'pricing' && (
                              <>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Plan Name</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.name || ''}
                                    onChange={(e) => handleItemChange(idx, 'name', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Price</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.price || ''}
                                    onChange={(e) => handleItemChange(idx, 'price', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div>
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Period (e.g. month)</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={item.period || ''}
                                    onChange={(e) => handleItemChange(idx, 'period', e.target.value)}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                                <div className="md:col-span-2">
                                  <label className="block text-[11px] font-bold text-gray-500 uppercase">Features (comma separated)</label>
                                  <input
                                    type="text"
                                    className="input-field py-1 px-2 text-sm"
                                    value={Array.isArray(item.features) ? item.features.join(', ') : item.features || ''}
                                    onChange={(e) => handleItemChange(idx, 'features', e.target.value.split(',').map(f => f.trim()))}
                                    onBlur={handleItemBlur}
                                  />
                                </div>
                              </>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Booking Service List Editor */}
                {activeSection.type === 'booking' && (
                  <div className="space-y-4 border-t border-gray-100 pt-6 mt-6">
                    <div className="flex items-center justify-between">
                      <label className="block text-sm font-semibold text-gray-700">Offered Services ({activeItems.length})</label>
                      <button
                        onClick={addBookingService}
                        className="btn-sm btn-secondary flex items-center gap-1 text-xs py-1"
                      >
                        <Plus size={14} /> Add Service
                      </button>
                    </div>

                    <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                      {activeItems.map((service, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <input
                            type="text"
                            className="input-field py-1.5 px-3 text-sm flex-1"
                            value={service || ''}
                            onChange={(e) => handleBookingServiceChange(idx, e.target.value)}
                            onBlur={handleBookingServiceBlur}
                          />
                          <button
                            onClick={() => removeBookingService(idx)}
                            className="text-gray-400 hover:text-red-500 p-2 rounded-lg hover:bg-gray-100 transition-all duration-200"
                            title="Delete Service"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

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

        {/* RIGHT: Dynamic Preview Panel */}
        <div className="space-y-6">
          <div className="card-hover">
            <h3 className="heading-3 mb-6 flex items-center gap-2">
              <Eye size={20} className="text-blue-500" /> Section Preview & Navigation
            </h3>

            {/* Schema summary cards */}
            <div className="space-y-4">
              {/* Dynamic preview card */}
              {activeSection && (
                <div className="rounded-xl overflow-hidden border border-gray-100 shadow-sm">
                  <div
                    className="p-6 transition-all duration-300"
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
                      <div className="flex items-center gap-2 mb-2">
                        {getSectionIcon(activeSection.type)}
                        <span className="text-xs font-semibold uppercase tracking-widest opacity-80 font-mono">
                          {activeVariant || activeSection.variant || 'default'}
                        </span>
                      </div>
                      
                      {activeTitle && (
                        <h2 className="text-xl font-bold mb-1">{activeTitle}</h2>
                      )}
                      
                      {activeSubtitle && (
                        <p className="text-sm opacity-80 mb-4">{activeSubtitle}</p>
                      )}

                      {activeCta && (
                        <div className="inline-block px-4 py-2 bg-white/20 backdrop-blur rounded-lg text-sm font-semibold mb-2">
                          {activeCta}
                        </div>
                      )}

                      {/* Display items summary if list exists */}
                      {['services', 'testimonials', 'team', 'pricing'].includes(activeSection.type) && activeItems && activeItems.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-white/10 space-y-2">
                          <p className="text-xs font-semibold opacity-70 uppercase tracking-wider">Items List ({activeItems.length})</p>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            {activeItems.slice(0, 4).map((item, idx) => (
                              <div key={idx} className="bg-white/10 rounded p-2 backdrop-blur-sm">
                                <p className="font-bold truncate">{item.name || `Item #${idx + 1}`}</p>
                                <p className="opacity-80 truncate">{item.role || item.price || item.description || ''}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Display booking services preview */}
                      {activeSection.type === 'booking' && activeItems && activeItems.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-white/10 space-y-2">
                          <p className="text-xs font-semibold opacity-70 uppercase tracking-wider">Services List ({activeItems.length})</p>
                          <div className="flex flex-wrap gap-1">
                            {activeItems.map((service, idx) => (
                              <span key={idx} className="bg-white/15 px-2 py-0.5 rounded text-[11px] font-medium backdrop-blur-sm">
                                {service}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Interactive Section Selector list */}
              <div>
                <h4 className="text-sm font-semibold text-gray-600 mb-3">All Sections (Click to edit)</h4>
                <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
                  {(schema.sections || []).map((section, idx) => (
                    <button
                      key={section.id || idx}
                      onClick={() => setSelectedSectionId(section.id)}
                      className={`w-full text-left flex items-center justify-between px-4 py-3 rounded-xl border transition-all duration-200 ${
                        selectedSectionId === section.id
                          ? 'bg-violet-50 border-violet-200 shadow-sm ring-1 ring-violet-200'
                          : 'bg-gray-50 border-gray-100 hover:border-gray-200'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className={`w-6 h-6 text-xs rounded-lg flex items-center justify-center font-bold ${
                          selectedSectionId === section.id
                            ? 'bg-violet-500 text-white'
                            : 'bg-gradient-to-br from-blue-500 to-indigo-500 text-white'
                        }`}>
                          {idx + 1}
                        </span>
                        <div>
                          <p className="text-sm font-semibold text-gray-800">{section.id}</p>
                          <p className="text-xs text-gray-500">{section.type} · {section.variant || 'default'}</p>
                        </div>
                      </div>
                      <span className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">
                        {selectedSectionId === section.id ? 'Active' : 'Select'}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Add New Section Controls */}
              <div className="border-t border-gray-100 pt-4">
                <h4 className="text-sm font-semibold text-gray-600 mb-2">Add New Section</h4>
                <div className="grid grid-cols-2 gap-2">
                  {['services', 'testimonials', 'team', 'booking', 'gallery', 'pricing', 'cta', 'contact'].map((type) => (
                    <button
                      key={type}
                      onClick={() => handleAddSection(type)}
                      className="px-3 py-2 rounded-xl text-xs font-semibold border border-gray-200 bg-white hover:bg-violet-50 hover:border-violet-300 hover:text-violet-700 text-gray-600 text-center transition-all duration-200"
                    >
                      + {type.toUpperCase()}
                    </button>
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
