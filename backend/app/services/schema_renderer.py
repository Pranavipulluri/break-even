"""
SchemaRenderer — Deterministic Schema-to-HTML Compiler.

CRITICAL RULE: Same schema → same output. ALWAYS.

Architecture:
    Schema → Component Mapper → HTML Templates → Compiled Website

This renderer reads a JSON website schema and compiles it into a gorgeous,
fully responsive, modern HTML page. It uses Tailwind CSS CDN and FontAwesome
for premium visual output. NO AI rendering logic inside — purely deterministic
template mapping.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SchemaRenderer:

    # ================================================================
    # Color Palettes — Design Token System
    # ================================================================

    COLOR_PALETTES = {
        "rose-gold-luxury": {
            "primary": "#b76e79",
            "secondary": "#3d3234",
            "accent": "#e4b4b8",
            "bg_light": "#faf3f3",
            "text_dark": "#2d2426",
            "text_light": "#ffffff",
            "gradient": "linear-gradient(135deg, #b76e79 0%, #e4b4b8 100%)",
        },
        "spa-serenity": {
            "primary": "#8fa89b",
            "secondary": "#2c3b35",
            "accent": "#d0dfd8",
            "bg_light": "#f4f7f6",
            "text_dark": "#1d2622",
            "text_light": "#ffffff",
            "gradient": "linear-gradient(135deg, #8fa89b 0%, #d0dfd8 100%)",
        },
        "lavender-luxury": {
            "primary": "#a799b7",
            "secondary": "#2d2430",
            "accent": "#d6cbd9",
            "bg_light": "#fdfbfd",
            "text_dark": "#1c1420",
            "text_light": "#ffffff",
            "gradient": "linear-gradient(135deg, #a799b7 0%, #d6cbd9 100%)",
        },
        "royal-navy": {
            "primary": "#1d2a44",
            "secondary": "#0c1524",
            "accent": "#3b5998",
            "bg_light": "#f5f7fa",
            "text_dark": "#0c1524",
            "text_light": "#ffffff",
            "gradient": "linear-gradient(135deg, #1d2a44 0%, #3b5998 100%)",
        },
        "emerald-gold": {
            "primary": "#044a27",
            "secondary": "#112217",
            "accent": "#d4af37",
            "bg_light": "#fcfbf7",
            "text_dark": "#112217",
            "text_light": "#ffffff",
            "gradient": "linear-gradient(135deg, #044a27 0%, #d4af37 100%)",
        },
    }

    # ================================================================
    # Component Template Registry — deterministic mapper
    # ================================================================

    COMPONENT_MAP = {
        "hero": "_render_hero",
        "services": "_render_services",
        "testimonials": "_render_testimonials",
        "team": "_render_team",
        "booking": "_render_booking",
        "contact": "_render_contact",
        "footer": "_render_footer",
        "gallery": "_render_gallery",
        "cta": "_render_cta",
        "pricing": "_render_pricing",
    }

    # ================================================================
    # Main render entry point
    # ================================================================

    @classmethod
    def render(cls, schema):
        """
        Compiles a dynamic component graph (WebsiteSchema dict) to a
        fully responsive, premium static HTML page.
        """
        if not isinstance(schema, dict):
            schema = schema.to_dict()

        seo = schema.get("seo", {})
        title = seo.get("title", "Break-Even Business Site")
        description = seo.get("description", "AI-powered small business management platform.")
        keywords = seo.get("keywords", "business, website, AI, booking, analytics")

        theme = schema.get("theme", {})
        palette_name = theme.get("palette", "spa-serenity")
        palette = cls.COLOR_PALETTES.get(palette_name, cls.COLOR_PALETTES["spa-serenity"])
        font_family = theme.get("font", "Inter")

        css_block = cls._compile_css(palette, font_family)
        navbar_html = cls._compile_navbar(schema)

        # Deterministic section compilation via component registry
        sections_html = ""
        for section in schema.get("sections", []):
            sections_html += cls._compile_section(section, palette)

        schema_version = schema.get("schema_version", schema.get("version", 1))

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="generator" content="Break-Even AI Business OS v{schema_version}">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome for Premium Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '{palette["primary"]}',
                        secondary: '{palette["secondary"]}',
                        accent: '{palette["accent"]}',
                        bgLight: '{palette["bg_light"]}',
                        textDark: '{palette["text_dark"]}'
                    }}
                }}
            }}
        }}
    </script>
    <style>
        {css_block}
    </style>
</head>
<body class="bg-bgLight font-sans antialiased text-textDark">
    {navbar_html}

    <main>
        {sections_html}
    </main>

    <!-- Unified Form Submission & Interactivity Scripts -->
    <script>
        // Custom notification banner
        function showNotification(message, isError = false) {{
            const notification = document.createElement("div");
            notification.className = `fixed bottom-5 right-5 px-6 py-4 rounded-xl shadow-2xl text-white font-semibold z-50 transition-all duration-300 transform translate-y-10 opacity-0 ${{isError ? 'bg-red-500' : 'bg-green-500'}}`;
            notification.innerText = message;
            document.body.appendChild(notification);

            setTimeout(() => {{
                notification.classList.remove("translate-y-10", "opacity-0");
            }}, 100);

            setTimeout(() => {{
                notification.classList.add("translate-y-10", "opacity-0");
                setTimeout(() => notification.remove(), 300);
            }}, 4000);
        }}

        // Booking submission
        async function submitBooking(event, businessId) {{
            event.preventDefault();
            const form = event.target;
            const data = {{
                business_id: businessId,
                customer_name: form.name.value,
                customer_email: form.email.value,
                customer_phone: form.phone.value || '',
                service_type: form.service.value,
                date: form.date.value,
                time: form.time.value,
                notes: form.notes ? form.notes.value : ''
            }};

            try {{
                const res = await fetch('/api/public/submit-consultation', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data)
                }});
                const result = await res.json();
                if (result.success) {{
                    showNotification("Appointment booked successfully! A confirmation email has been sent.");
                    form.reset();
                }} else {{
                    showNotification(result.error || "Booking failed. Please try again.", true);
                }}
            }} catch (err) {{
                showNotification("A network error occurred. Please try again.", true);
            }}
        }}

        // Contact submission
        async function submitContact(event, businessId) {{
            event.preventDefault();
            const form = event.target;
            const data = {{
                business_id: businessId,
                name: form.name.value,
                email: form.email.value,
                subject: form.subject ? form.subject.value : 'General Inquiry',
                message: form.message.value
            }};

            try {{
                const res = await fetch('/api/public/submit-contact', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data)
                }});
                const result = await res.json();
                if (result.success) {{
                    showNotification("Message sent successfully! We will contact you soon.");
                    form.reset();
                }} else {{
                    showNotification(result.error || "Message failed to send.", true);
                }}
            }} catch (err) {{
                showNotification("A network error occurred.", true);
            }}
        }}
    </script>
</body>
</html>
'''
        # Inject child→parent analytics tracking snippet
        try:
            from app.services.tracking_snippet import TrackingSnippet
            business_id = schema.get("business_id", "")
            html = TrackingSnippet.inject(html, business_id=business_id)
        except Exception as e:
            logger.warning(f"Could not inject tracking snippet: {e}")

        return html

    # ================================================================
    # CSS Compilation — design token system
    # ================================================================

    @classmethod
    def _compile_css(cls, palette, font_family):
        return f'''
        :root {{
            --primary: {palette["primary"]};
            --secondary: {palette["secondary"]};
            --accent: {palette["accent"]};
            --bg-light: {palette["bg_light"]};
            --text-dark: {palette["text_dark"]};
            --text-light: {palette["text_light"]};
            --gradient: {palette["gradient"]};
        }}
        body {{
            font-family: '{font_family}', sans-serif;
            background-color: var(--bg-light);
            color: var(--text-dark);
        }}
        .premium-btn {{
            background: var(--gradient);
            color: var(--text-light);
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }}
        .premium-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
            filter: brightness(1.05);
        }}
        .card-hover {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .card-hover:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06);
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .animate-fade-in-up {{
            animation: fadeInUp 0.6s ease-out both;
        }}
        '''

    # ================================================================
    # Navbar
    # ================================================================

    @classmethod
    def _compile_navbar(cls, schema):
        seo = schema.get("seo", {})
        title = seo.get("title", "Break-Even Business")
        sections = schema.get("sections", [])

        nav_links = ""
        for sec in sections:
            sec_type = sec.get("type")
            if sec_type in ["services", "testimonials", "team", "booking", "contact", "gallery", "pricing"]:
                label = sec_type.capitalize()
                nav_links += f'<a href="#{sec_type}" class="text-sm font-semibold hover:text-primary transition">{label}</a>'

        return f'''
        <nav class="sticky top-0 bg-white/80 backdrop-blur-md border-b border-gray-100 z-40">
            <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                <a href="#" class="flex items-center space-x-3">
                    <span class="text-2xl font-bold tracking-tight text-textDark bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">{title}</span>
                </a>
                <div class="hidden md:flex items-center space-x-8">
                    {nav_links}
                    <a href="#booking" class="premium-btn px-6 py-3 rounded-full text-sm font-semibold">Book Online</a>
                </div>
                <button id="mobile-menu-btn" class="md:hidden text-textDark" onclick="document.getElementById('mobile-menu').classList.toggle('hidden')">
                    <i class="fas fa-bars text-xl"></i>
                </button>
            </div>
            <div id="mobile-menu" class="hidden md:hidden bg-white/95 backdrop-blur-md border-t border-gray-100 px-6 py-4 space-y-3">
                {nav_links.replace('class="text-sm', 'class="block text-sm')}
                <a href="#booking" class="premium-btn block text-center px-6 py-3 rounded-full text-sm font-semibold mt-2">Book Online</a>
            </div>
        </nav>
        '''

    # ================================================================
    # Section dispatcher — uses COMPONENT_MAP registry
    # ================================================================

    @classmethod
    def _compile_section(cls, section, palette):
        sec_type = section.get("type")
        render_method_name = cls.COMPONENT_MAP.get(sec_type)
        if render_method_name:
            render_method = getattr(cls, render_method_name)
            return render_method(
                section.get("id"),
                section.get("variant", f"{sec_type}-split"),
                section.get("content", {}),
                palette,
            )
        return ""

    # ================================================================
    # HERO Section
    # ================================================================

    @classmethod
    def _render_hero(cls, sec_id, variant, content, palette):
        title = content.get("title", "Premium Services Built Around You")
        subtitle = content.get("subtitle", "Highly dedicated services driven by elegance, precision, and state-of-the-art experiences.")
        cta = content.get("cta", "Book Appointment")
        image = content.get("image", "https://images.unsplash.com/photo-1540555700478-4be289fbecef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80")

        if variant == "hero-split":
            return f'''
            <section id="{sec_id}" class="py-20 lg:py-32 max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center animate-fade-in-up">
                <div class="space-y-8">
                    <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-textDark tracking-tight leading-tight">{title}</h1>
                    <p class="text-lg text-gray-600 leading-relaxed max-w-xl">{subtitle}</p>
                    <div class="flex flex-col sm:flex-row gap-4 pt-4">
                        <a href="#booking" class="premium-btn text-center px-8 py-4 rounded-full text-base font-bold">{cta}</a>
                        <a href="#services" class="border border-gray-300 text-center text-textDark hover:bg-gray-50 transition px-8 py-4 rounded-full text-base font-bold">Our Services</a>
                    </div>
                </div>
                <div class="relative">
                    <div class="absolute inset-0 bg-accent/20 rounded-3xl blur-2xl transform rotate-6 scale-95"></div>
                    <img src="{image}" alt="Hero Image" class="relative rounded-3xl shadow-2xl object-cover w-full h-[500px]" loading="lazy">
                </div>
            </section>
            '''
        elif variant == "hero-centered":
            return f'''
            <section id="{sec_id}" class="py-24 lg:py-36 max-w-4xl mx-auto px-6 text-center space-y-10 animate-fade-in-up">
                <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-textDark tracking-tight leading-tight">{title}</h1>
                <p class="text-xl text-gray-600 leading-relaxed max-w-2xl mx-auto">{subtitle}</p>
                <div class="flex justify-center gap-4 pt-4">
                    <a href="#booking" class="premium-btn px-8 py-4 rounded-full text-base font-bold">{cta}</a>
                </div>
            </section>
            '''
        elif variant == "hero-luxury":
            return f'''
            <section id="{sec_id}" class="relative min-h-[80vh] flex items-center justify-center overflow-hidden animate-fade-in-up">
                <div class="absolute inset-0">
                    <img src="{image}" alt="Hero Background" class="w-full h-full object-cover" loading="lazy">
                    <div class="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/70"></div>
                </div>
                <div class="relative z-10 text-center max-w-4xl mx-auto px-6 space-y-8">
                    <h1 class="text-4xl sm:text-5xl lg:text-7xl font-extrabold text-white tracking-tight leading-tight drop-shadow-lg">{title}</h1>
                    <p class="text-xl text-white/90 leading-relaxed max-w-2xl mx-auto">{subtitle}</p>
                    <div class="flex justify-center gap-4 pt-6">
                        <a href="#booking" class="premium-btn px-10 py-5 rounded-full text-lg font-bold shadow-2xl">{cta}</a>
                    </div>
                </div>
            </section>
            '''
        # Fallback: hero-minimal
        return f'''
        <section id="{sec_id}" class="py-16 max-w-3xl mx-auto px-6 text-center space-y-6 animate-fade-in-up">
            <h1 class="text-3xl sm:text-4xl font-bold text-textDark">{title}</h1>
            <p class="text-base text-gray-600">{subtitle}</p>
            <a href="#booking" class="premium-btn inline-block px-6 py-3 rounded-full font-bold">{cta}</a>
        </section>
        '''

    # ================================================================
    # SERVICES Section
    # ================================================================

    @classmethod
    def _render_services(cls, sec_id, variant, content, palette):
        title = content.get("title", "Experience Premium Services")
        items = content.get("items", [])

        if not items:
            items = [
                {"name": "Bespoke Treatment", "price": "$120", "description": "Highly customized personal care sessions crafted for premium relaxation."},
                {"name": "Essential Consultation", "price": "$80", "description": "Focused insights and strategies to structure and achieve optimal results."},
                {"name": "Comprehensive Session", "price": "$200", "description": "Full-immersion treatment package including all amenities."},
            ]

        items_html = ""
        for item in items:
            price_tag = f'<span class="text-primary font-bold text-lg">{item.get("price", "")}</span>' if item.get("price") else ""
            icon = item.get("icon", "fas fa-spa")
            items_html += f'''
            <div class="card-hover bg-white rounded-2xl p-8 border border-gray-100 shadow-sm flex flex-col justify-between">
                <div>
                    <div class="h-12 w-12 bg-accent/20 rounded-xl flex items-center justify-center text-primary mb-4">
                        <i class="{icon}"></i>
                    </div>
                    <div class="flex justify-between items-start mb-4">
                        <h3 class="text-xl font-bold text-textDark">{item.get("name")}</h3>
                        {price_tag}
                    </div>
                    <p class="text-gray-600 text-sm leading-relaxed mb-6">{item.get("description", "")}</p>
                </div>
                <a href="#booking" class="text-primary font-semibold hover:text-secondary flex items-center gap-2 mt-auto text-sm transition">
                    Book Now <i class="fas fa-arrow-right text-xs"></i>
                </a>
            </div>
            '''

        return f'''
        <section id="services" class="py-20 bg-gray-50/50">
            <div class="max-w-7xl mx-auto px-6">
                <div class="text-center space-y-4 mb-16">
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-textDark tracking-tight">{title}</h2>
                    <div class="w-16 h-1 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
                </div>
                <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {items_html}
                </div>
            </div>
        </section>
        '''

    # ================================================================
    # TESTIMONIALS Section
    # ================================================================

    @classmethod
    def _render_testimonials(cls, sec_id, variant, content, palette):
        title = content.get("title", "What Our Clients Say")
        items = content.get("items", [])

        if not items:
            items = [
                {"name": "Eleanor Vance", "role": "Premium Member", "quote": "The attention to detail and professional environment exceeded every expectation."},
                {"name": "Marcus Aurelius", "role": "Strategic Advisor", "quote": "I appreciate the continuous refinement and premium care standard."},
            ]

        items_html = ""
        for item in items:
            items_html += f'''
            <div class="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm space-y-6">
                <div class="flex space-x-1 text-amber-400">
                    <i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i><i class="fas fa-star"></i>
                </div>
                <p class="text-gray-600 italic leading-relaxed">"{item.get("quote")}"</p>
                <div class="flex items-center space-x-4 pt-4 border-t border-gray-50">
                    <div>
                        <h4 class="font-bold text-textDark">{item.get("name")}</h4>
                        <span class="text-xs text-gray-500">{item.get("role", "")}</span>
                    </div>
                </div>
            </div>
            '''

        return f'''
        <section id="testimonials" class="py-20 max-w-7xl mx-auto px-6">
            <div class="text-center space-y-4 mb-16">
                <h2 class="text-3xl sm:text-4xl font-extrabold text-textDark tracking-tight">{title}</h2>
                <div class="w-16 h-1 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
            </div>
            <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                {items_html}
            </div>
        </section>
        '''

    # ================================================================
    # TEAM Section
    # ================================================================

    @classmethod
    def _render_team(cls, sec_id, variant, content, palette):
        title = content.get("title", "Meet Our Specialists")
        members = content.get("members", [])

        if not members:
            members = [
                {"name": "Sophia Lauren", "role": "Senior Consultant", "bio": "Over 12 years of hands-on expertise.", "photo": "https://images.unsplash.com/photo-1494790108755-2616b612b786?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80"},
                {"name": "David Miller", "role": "Creative Specialist", "bio": "Passionately tailoring unique portfolios.", "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80"},
            ]

        members_html = ""
        for item in members:
            members_html += f'''
            <div class="card-hover bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm">
                <img src="{item.get("photo")}" alt="{item.get("name")}" class="w-full h-72 object-cover" loading="lazy">
                <div class="p-8 space-y-3">
                    <h3 class="text-xl font-bold text-textDark">{item.get("name")}</h3>
                    <p class="text-primary font-semibold text-sm">{item.get("role")}</p>
                    <p class="text-gray-600 text-sm leading-relaxed">{item.get("bio", "")}</p>
                </div>
            </div>
            '''

        return f'''
        <section id="team" class="py-20 bg-gray-50/50">
            <div class="max-w-7xl mx-auto px-6">
                <div class="text-center space-y-4 mb-16">
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-textDark tracking-tight">{title}</h2>
                    <div class="w-16 h-1 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
                </div>
                <div class="grid md:grid-cols-2 gap-8 max-w-2xl mx-auto">
                    {members_html}
                </div>
            </div>
        </section>
        '''

    # ================================================================
    # BOOKING Section
    # ================================================================

    @classmethod
    def _render_booking(cls, sec_id, variant, content, palette):
        title = content.get("title", "Schedule an Appointment")
        business_id = content.get("business_id", "default_business")
        services_list = content.get("services", ["General Consultation", "Premium Service"])

        services_options = ""
        for s in services_list:
            services_options += f'<option value="{s}">{s}</option>'

        return f'''
        <section id="booking" class="py-20 max-w-7xl mx-auto px-6">
            <div class="text-center space-y-4 mb-16">
                <h2 class="text-3xl sm:text-4xl font-extrabold text-textDark tracking-tight">{title}</h2>
                <p class="text-gray-600 text-sm max-w-md mx-auto">Select your preferred date, time, and service package below.</p>
                <div class="w-16 h-1 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
            </div>

            <div class="bg-white rounded-3xl border border-gray-100 shadow-xl max-w-2xl mx-auto overflow-hidden">
                <div class="bg-gradient-to-r from-primary to-secondary p-8 text-white">
                    <h3 class="text-2xl font-bold">Reservation Desk</h3>
                    <p class="text-white/80 text-sm">Please fill in your details to secure your priority booking slot.</p>
                </div>
                <form onsubmit="submitBooking(event, '{business_id}')" class="p-8 space-y-6">
                    <div class="grid md:grid-cols-2 gap-6">
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Full Name</label>
                            <input type="text" name="name" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition">
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Email Address</label>
                            <input type="email" name="email" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition">
                        </div>
                    </div>
                    <div class="grid md:grid-cols-2 gap-6">
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Phone Number</label>
                            <input type="tel" name="phone" class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition">
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Service Package</label>
                            <select name="service" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm bg-white transition">
                                {services_options}
                            </select>
                        </div>
                    </div>
                    <div class="grid md:grid-cols-2 gap-6">
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Appointment Date</label>
                            <input type="date" name="date" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition">
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Preferred Time</label>
                            <input type="time" name="time" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition">
                        </div>
                    </div>
                    <div class="space-y-2">
                        <label class="text-sm font-semibold text-textDark">Additional Requests</label>
                        <textarea name="notes" rows="4" class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition" placeholder="Any special needs or inquiries..."></textarea>
                    </div>
                    <button type="submit" class="premium-btn w-full py-4 rounded-xl text-base font-bold shadow-lg mt-4">Confirm Appointment Slot</button>
                </form>
            </div>
        </section>
        '''

    # ================================================================
    # CONTACT Section
    # ================================================================

    @classmethod
    def _render_contact(cls, sec_id, variant, content, palette):
        title = content.get("title", "Get in Touch")
        business_id = content.get("business_id", "default_business")
        address = content.get("address", "123 Elegance Blvd, Luxury Suite 404")
        phone = content.get("phone", "(555) 019-2834")
        email = content.get("email", "contact@business.com")

        return f'''
        <section id="contact" class="py-20 bg-gray-50/50">
            <div class="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16">
                <div class="space-y-8">
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-textDark tracking-tight">{title}</h2>
                    <p class="text-gray-600 leading-relaxed max-w-md">Our customer concierge team is available to assist you. Drop a message or contact us directly.</p>

                    <div class="space-y-6">
                        <div class="flex items-start space-x-4">
                            <div class="h-12 w-12 bg-white border border-gray-100 rounded-xl flex items-center justify-center text-primary shadow-sm">
                                <i class="fas fa-map-marker-alt"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-textDark">Office Address</h4>
                                <span class="text-sm text-gray-500">{address}</span>
                            </div>
                        </div>
                        <div class="flex items-start space-x-4">
                            <div class="h-12 w-12 bg-white border border-gray-100 rounded-xl flex items-center justify-center text-primary shadow-sm">
                                <i class="fas fa-phone-alt"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-textDark">Phone Support</h4>
                                <span class="text-sm text-gray-500">{phone}</span>
                            </div>
                        </div>
                        <div class="flex items-start space-x-4">
                            <div class="h-12 w-12 bg-white border border-gray-100 rounded-xl flex items-center justify-center text-primary shadow-sm">
                                <i class="fas fa-envelope"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-textDark">Email Desk</h4>
                                <span class="text-sm text-gray-500">{email}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-3xl border border-gray-100 shadow-xl p-8">
                    <h3 class="text-xl font-bold text-textDark mb-6">Send Message</h3>
                    <form onsubmit="submitContact(event, '{business_id}')" class="space-y-6">
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Your Name</label>
                            <input type="text" name="name" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition">
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Email Address</label>
                            <input type="email" name="email" required class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition">
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Message Subject</label>
                            <input type="text" name="subject" class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition" placeholder="How can we help?">
                        </div>
                        <div class="space-y-2">
                            <label class="text-sm font-semibold text-textDark">Message</label>
                            <textarea name="message" required rows="4" class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:outline-none text-sm transition" placeholder="Write your inquiry here..."></textarea>
                        </div>
                        <button type="submit" class="premium-btn w-full py-4 rounded-xl text-sm font-bold shadow-md">Send Inquiry Message</button>
                    </form>
                </div>
            </div>
        </section>
        '''

    # ================================================================
    # FOOTER Section
    # ================================================================

    @classmethod
    def _render_footer(cls, sec_id, variant, content, palette):
        current_year = datetime.now().year
        return f'''
        <footer id="{sec_id}" class="py-12 bg-textDark text-white/60 text-center text-sm border-t border-white/5">
            <div class="max-w-7xl mx-auto px-6 space-y-4">
                <div class="flex justify-center space-x-6 text-white/80">
                    <a href="#" class="hover:text-primary transition"><i class="fab fa-instagram text-lg"></i></a>
                    <a href="#" class="hover:text-primary transition"><i class="fab fa-facebook text-lg"></i></a>
                    <a href="#" class="hover:text-primary transition"><i class="fab fa-twitter text-lg"></i></a>
                </div>
                <p class="pt-4 border-t border-white/5">&copy; {current_year} All Rights Reserved. Powered by Break-Even AI Business Platform.</p>
            </div>
        </footer>
        '''

    # ================================================================
    # GALLERY Section (NEW)
    # ================================================================

    @classmethod
    def _render_gallery(cls, sec_id, variant, content, palette):
        title = content.get("title", "Our Gallery")
        images = content.get("images", [])

        if not images:
            images = [
                {"url": "https://images.unsplash.com/photo-1560066984-138dadb4c035?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", "alt": "Gallery 1"},
                {"url": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", "alt": "Gallery 2"},
                {"url": "https://images.unsplash.com/photo-1519823551278-64ac92734fb1?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", "alt": "Gallery 3"},
                {"url": "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", "alt": "Gallery 4"},
                {"url": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", "alt": "Gallery 5"},
                {"url": "https://images.unsplash.com/photo-1600334089648-b0d9d3028eb2?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", "alt": "Gallery 6"},
            ]

        grid_class = "grid grid-cols-2 md:grid-cols-3 gap-4"
        if variant == "gallery-masonry":
            grid_class = "columns-2 md:columns-3 gap-4 space-y-4"

        images_html = ""
        for img in images:
            images_html += f'''
            <div class="card-hover overflow-hidden rounded-2xl">
                <img src="{img.get("url")}" alt="{img.get("alt", "Gallery image")}" class="w-full h-64 object-cover hover:scale-105 transition-transform duration-500" loading="lazy">
            </div>
            '''

        return f'''
        <section id="gallery" class="py-20">
            <div class="max-w-7xl mx-auto px-6">
                <div class="text-center space-y-4 mb-16">
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-textDark tracking-tight">{title}</h2>
                    <div class="w-16 h-1 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
                </div>
                <div class="{grid_class}">
                    {images_html}
                </div>
            </div>
        </section>
        '''

    # ================================================================
    # CTA Section (NEW)
    # ================================================================

    @classmethod
    def _render_cta(cls, sec_id, variant, content, palette):
        title = content.get("title", "Ready to Get Started?")
        subtitle = content.get("subtitle", "Book your appointment today and experience the difference.")
        cta = content.get("cta", "Book Now")

        if variant == "cta-banner":
            return f'''
            <section id="{sec_id}" class="py-20">
                <div class="max-w-7xl mx-auto px-6">
                    <div class="bg-gradient-to-r from-primary to-secondary rounded-3xl p-12 lg:p-16 text-center text-white shadow-2xl">
                        <h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight mb-4">{title}</h2>
                        <p class="text-white/80 text-lg max-w-xl mx-auto mb-8">{subtitle}</p>
                        <a href="#booking" class="inline-block bg-white text-primary px-10 py-4 rounded-full font-bold text-base hover:bg-gray-100 transition shadow-lg">{cta}</a>
                    </div>
                </div>
            </section>
            '''
        elif variant == "cta-card":
            return f'''
            <section id="{sec_id}" class="py-20 max-w-4xl mx-auto px-6">
                <div class="bg-white rounded-3xl border border-gray-100 shadow-xl p-12 text-center space-y-6">
                    <h2 class="text-3xl font-extrabold text-textDark tracking-tight">{title}</h2>
                    <p class="text-gray-600 max-w-md mx-auto">{subtitle}</p>
                    <a href="#booking" class="premium-btn inline-block px-10 py-4 rounded-full font-bold text-base">{cta}</a>
                </div>
            </section>
            '''
        # cta-floating
        return f'''
        <section id="{sec_id}" class="py-16 max-w-3xl mx-auto px-6 text-center space-y-6">
            <h2 class="text-2xl sm:text-3xl font-bold text-textDark">{title}</h2>
            <p class="text-gray-600">{subtitle}</p>
            <a href="#booking" class="premium-btn inline-block px-8 py-3 rounded-full font-bold">{cta}</a>
        </section>
        '''

    # ================================================================
    # PRICING Section (NEW)
    # ================================================================

    @classmethod
    def _render_pricing(cls, sec_id, variant, content, palette):
        title = content.get("title", "Our Pricing Plans")
        plans = content.get("plans", [])

        if not plans:
            plans = [
                {"name": "Essential", "price": "$79", "period": "/session", "features": ["60-min treatment", "Basic consultation", "Relaxation room access"], "highlight": False},
                {"name": "Premium", "price": "$149", "period": "/session", "features": ["90-min treatment", "Full consultation", "Luxury amenities", "Priority booking"], "highlight": True},
                {"name": "Elite", "price": "$249", "period": "/session", "features": ["120-min treatment", "VIP consultation", "All amenities", "Take-home kit", "Dedicated therapist"], "highlight": False},
            ]

        plans_html = ""
        for plan in plans:
            highlight = plan.get("highlight", False)
            border_class = "border-primary shadow-xl scale-105" if highlight else "border-gray-100 shadow-sm"
            badge = '<span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-white text-xs font-bold px-4 py-1 rounded-full">Most Popular</span>' if highlight else ""
            features_html = ""
            for feat in plan.get("features", []):
                features_html += f'<li class="flex items-center gap-3 text-sm text-gray-600"><i class="fas fa-check text-primary text-xs"></i>{feat}</li>'

            plans_html += f'''
            <div class="relative card-hover bg-white rounded-2xl border {border_class} p-8 flex flex-col">
                {badge}
                <h3 class="text-xl font-bold text-textDark mb-2">{plan.get("name")}</h3>
                <div class="mb-6">
                    <span class="text-4xl font-extrabold text-textDark">{plan.get("price")}</span>
                    <span class="text-gray-500 text-sm">{plan.get("period", "")}</span>
                </div>
                <ul class="space-y-3 mb-8 flex-grow">
                    {features_html}
                </ul>
                <a href="#booking" class="premium-btn block text-center py-3 rounded-xl font-bold text-sm">Choose Plan</a>
            </div>
            '''

        return f'''
        <section id="pricing" class="py-20 bg-gray-50/50">
            <div class="max-w-7xl mx-auto px-6">
                <div class="text-center space-y-4 mb-16">
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-textDark tracking-tight">{title}</h2>
                    <div class="w-16 h-1 bg-gradient-to-r from-primary to-secondary mx-auto rounded-full"></div>
                </div>
                <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto items-start">
                    {plans_html}
                </div>
            </div>
        </section>
        '''
