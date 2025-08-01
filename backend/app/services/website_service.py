import openai
from flask import current_app
import json
from datetime import datetime

class WebsiteService:
    def __init__(self):
        openai.api_key = current_app.config.get('OPENAI_API_KEY')
        self.use_openai = bool(openai.api_key)
    
    def generate_website_content(self, business_type, business_name, description, area):
        """Generate website content using AI"""
        try:
            if self.use_openai:
                return self._generate_with_openai(business_type, business_name, description, area)
            else:
                return self._generate_template_content(business_type, business_name, description, area)
        except Exception as e:
            print(f"Error generating website content: {e}")
            return self._generate_template_content(business_type, business_name, description, area)
    
    def _generate_with_openai(self, business_type, business_name, description, area):
        """Generate content using OpenAI"""
        prompt = f"""
        Create website content for a {business_type} business called "{business_name}" located in {area}.
        Business description: {description}
        
        Generate the following content in JSON format:
        {{
            "hero_title": "Main headline for the website",
            "hero_subtitle": "Subtitle or tagline",
            "about_title": "About Us section title",
            "about_content": "About us paragraph content",
            "services_title": "Services/Products section title",
            "services": [
                {{"name": "Service 1", "description": "Service description"}},
                {{"name": "Service 2", "description": "Service description"}},
                {{"name": "Service 3", "description": "Service description"}}
            ],
            "contact_title": "Contact section title",
            "contact_description": "Why customers should contact us",
            "footer_text": "Footer description",
            "meta_keywords": ["keyword1", "keyword2", "keyword3"]
        }}
        
        Make the content engaging, professional, and specific to the business type and location.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional website content creator. Generate engaging, SEO-friendly content for small businesses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Extract content manually if JSON parsing fails
                return self._parse_openai_content(content, business_type, business_name, area)
                
        except Exception as e:
            print(f"OpenAI content generation failed: {e}")
            return self._generate_template_content(business_type, business_name, description, area)
    
    def _parse_openai_content(self, content, business_type, business_name, area):
        """Parse OpenAI response if JSON parsing fails"""
        # Basic parsing logic - you can improve this
        return {
            "hero_title": f"Welcome to {business_name}",
            "hero_subtitle": f"Your trusted {business_type} in {area}",
            "about_title": "About Us",
            "about_content": f"We are a professional {business_type} business serving the {area} community with excellence and dedication.",
            "services_title": "Our Services",
            "services": [
                {"name": "Service 1", "description": "High-quality service tailored to your needs"},
                {"name": "Service 2", "description": "Professional service with attention to detail"},
                {"name": "Service 3", "description": "Reliable service you can count on"}
            ],
            "contact_title": "Get In Touch",
            "contact_description": "Contact us today to learn more about our services",
            "footer_text": f"© 2024 {business_name}. Serving {area} with pride.",
            "meta_keywords": [business_type, area, "professional", "quality"]
        }
    
    def _generate_template_content(self, business_type, business_name, description, area):
        """Generate template content without AI"""
        templates = {
            'food_store': {
                "hero_title": f"Delicious Food at {business_name}",
                "hero_subtitle": f"Fresh, authentic cuisine in {area}",
                "about_title": "About Our Restaurant",
                "about_content": f"Welcome to {business_name}, where we serve the finest {business_type} cuisine in {area}. {description}",
                "services_title": "Our Menu",
                "services": [
                    {"name": "Appetizers", "description": "Fresh starters to begin your meal"},
                    {"name": "Main Courses", "description": "Hearty, delicious main dishes"},
                    {"name": "Desserts", "description": "Sweet treats to end your meal"}
                ],
                "contact_title": "Visit Us Today",
                "contact_description": "Come and experience the best food in town",
                "footer_text": f"© 2024 {business_name}. Serving delicious food in {area}.",
                "meta_keywords": ["restaurant", "food", area, "dining", "cuisine"]
            },
            'fashion': {
                "hero_title": f"Fashion Forward at {business_name}",
                "hero_subtitle": f"Style and elegance in {area}",
                "about_title": "About Our Store",
                "about_content": f"{business_name} is your premier fashion destination in {area}. {description}",
                "services_title": "Our Collections",
                "services": [
                    {"name": "Women's Fashion", "description": "Latest trends for women"},
                    {"name": "Men's Fashion", "description": "Stylish clothing for men"},
                    {"name": "Accessories", "description": "Complete your look with our accessories"}
                ],
                "contact_title": "Shop With Us",
                "contact_description": "Discover your new favorite style today",
                "footer_text": f"© 2024 {business_name}. Fashion excellence in {area}.",
                "meta_keywords": ["fashion", "clothing", area, "style", "trends"]
            },
            'professional': {
                "hero_title": f"Professional Services by {business_name}",
                "hero_subtitle": f"Expert solutions in {area}",
                "about_title": "About Our Services",
                "about_content": f"{business_name} provides professional {business_type} services in {area}. {description}",
                "services_title": "Our Expertise",
                "services": [
                    {"name": "Consultation", "description": "Expert advice for your needs"},
                    {"name": "Implementation", "description": "Professional execution of solutions"},
                    {"name": "Support", "description": "Ongoing support and maintenance"}
                ],
                "contact_title": "Contact Us",
                "contact_description": "Get in touch for professional service",
                "footer_text": f"© 2024 {business_name}. Professional excellence in {area}.",
                "meta_keywords": ["professional", "services", area, "expert", "business"]
            }
        }
        
        # Default template
        default_template = {
            "hero_title": f"Welcome to {business_name}",
            "hero_subtitle": f"Quality {business_type} services in {area}",
            "about_title": "About Us",
            "about_content": f"At {business_name}, we provide excellent {business_type} services in {area}. {description}",
            "services_title": "Our Services",
            "services": [
                {"name": "Service 1", "description": "Professional service with attention to detail"},
                {"name": "Service 2", "description": "Quality service you can trust"},
                {"name": "Service 3", "description": "Reliable service for all your needs"}
            ],
            "contact_title": "Get In Touch",
            "contact_description": "Contact us to learn more about our services",
            "footer_text": f"© 2024 {business_name}. Serving {area} with excellence.",
            "meta_keywords": [business_type, area, "professional", "quality", "service"]
        }
        
        return templates.get(business_type, default_template)
    
    def generate_website_html(self, website_data, content_data, products=None):
        """Generate complete HTML for child website"""
        theme_colors = self._get_theme_colors(website_data['color_theme'])
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content_data['hero_title']}</title>
    <meta name="description" content="{content_data.get('about_content', '')[:160]}">
    <meta name="keywords" content="{', '.join(content_data.get('meta_keywords', []))}">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <style>
        :root {{
            --primary-color: {theme_colors['primary']};
            --secondary-color: {theme_colors['secondary']};
            --background-color: {theme_colors['background']};
        }}
        
        .btn-primary {{
            background-color: var(--primary-color);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }}
        
        .btn-primary:hover {{
            opacity: 0.9;
            transform: translateY(-2px);
        }}
        
        .section-padding {{
            padding: 4rem 1rem;
        }}
        
        {website_data.get('custom_css', '')}
    </style>
</head>
<body style="background-color: var(--background-color);">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg fixed w-full top-0 z-50">
        <div class="max-w-6xl mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center">
                    {f'<img src="{website_data["logo_url"]}" alt="Logo" class="h-10 w-auto mr-3">' if website_data.get('logo_url') else ''}
                    <h1 class="text-2xl font-bold" style="color: var(--primary-color);">{website_data['website_name']}</h1>
                </div>
                <div class="hidden md:flex space-x-6">
                    <a href="#home" class="text-gray-700 hover:text-gray-900">Home</a>
                    <a href="#about" class="text-gray-700 hover:text-gray-900">About</a>
                    <a href="#services" class="text-gray-700 hover:text-gray-900">Services</a>
                    {f'<a href="#products" class="text-gray-700 hover:text-gray-900">Products</a>' if products else ''}
                    <a href="#contact" class="text-gray-700 hover:text-gray-900">Contact</a>
                </div>
                <button id="mobile-menu-btn" class="md:hidden">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                    </svg>
                </button>
            </div>
        </div>
        
        <!-- Mobile Menu -->
        <div id="mobile-menu" class="hidden md:hidden">
            <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t">
                <a href="#home" class="block px-3 py-2 text-gray-700">Home</a>
                <a href="#about" class="block px-3 py-2 text-gray-700">About</a>
                <a href="#services" class="block px-3 py-2 text-gray-700">Services</a>
                {f'<a href="#products" class="block px-3 py-2 text-gray-700">Products</a>' if products else ''}
                <a href="#contact" class="block px-3 py-2 text-gray-700">Contact</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="section-padding mt-20" style="background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));">
        <div class="max-w-6xl mx-auto text-center text-white">
            <h1 class="text-5xl font-bold mb-6">{content_data['hero_title']}</h1>
            <p class="text-xl mb-8">{content_data['hero_subtitle']}</p>
            <a href="#contact" class="btn-primary bg-white text-gray-800 hover:bg-gray-100">Get Started</a>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="section-padding bg-white">
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold mb-4" style="color: var(--primary-color);">{content_data['about_title']}</h2>
                <p class="text-lg text-gray-600 max-w-3xl mx-auto">{content_data['about_content']}</p>
            </div>
        </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="section-padding" style="background-color: var(--background-color);">
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold mb-4" style="color: var(--primary-color);">{content_data['services_title']}</h2>
            </div>
            <div class="grid md:grid-cols-3 gap-8">
                {self._generate_services_html(content_data['services'])}
            </div>
        </div>
    </section>

    {self._generate_products_html(products) if products else ''}

    <!-- Contact Section -->
    <section id="contact" class="section-padding bg-white">
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-12">
                <h2 class="text-4xl font-bold mb-4" style="color: var(--primary-color);">{content_data['contact_title']}</h2>
                <p class="text-lg text-gray-600">{content_data['contact_description']}</p>
            </div>
            
            <div class="grid md:grid-cols-2 gap-12">
                <!-- Contact Form -->
                <div>
                    <h3 class="text-2xl font-bold mb-6">Send us a message</h3>
                    <form id="contact-form" class="space-y-4">
                        <div>
                            <label class="block text-gray-700 font-medium mb-2">Name *</label>
                            <input type="text" name="name" required class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-gray-700 font-medium mb-2">Email *</label>
                            <input type="email" name="email" required class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-gray-700 font-medium mb-2">Phone</label>
                            <input type="tel" name="phone" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-gray-700 font-medium mb-2">Message *</label>
                            <textarea name="message" required rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
                        </div>
                        <button type="submit" class="btn-primary w-full">Send Message</button>
                    </form>
                </div>
                
                <!-- Contact Info -->
                <div>
                    <h3 class="text-2xl font-bold mb-6">Contact Information</h3>
                    <div class="space-y-4">
                        {self._generate_contact_info_html(website_data['contact_info'])}
                    </div>
                    
                    <!-- Newsletter Signup -->
                    <div class="mt-8 p-6 bg-gray-50 rounded-lg">
                        <h4 class="text-lg font-bold mb-4">Stay Updated</h4>
                        <p class="text-gray-600 mb-4">Subscribe to receive updates and special offers.</p>
                        <form id="newsletter-form" class="flex">
                            <input type="email" name="email" placeholder="Your email" required class="flex-1 p-3 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500">
                            <button type="submit" class="btn-primary rounded-l-none">Subscribe</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <p>{content_data['footer_text']}</p>
            <p class="mt-2 text-gray-400">Powered by Break-even Platform</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script>
        // Mobile menu toggle
        document.getElementById('mobile-menu-btn').addEventListener('click', function() {{
            const mobileMenu = document.getElementById('mobile-menu');
            mobileMenu.classList.toggle('hidden');
        }});

        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});

        // Contact form submission
        document.getElementById('contact-form').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {{
                recipient_id: '{website_data["owner_id"]}',
                customer_name: formData.get('name'),
                customer_email: formData.get('email'),
                customer_phone: formData.get('phone'),
                content: formData.get('message'),
                message_type: 'contact_form',
                website_id: '{website_data.get("_id", "")}'
            }};
            
            try {{
                const response = await fetch('/api/messages', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(data)
                }});
                
                if (response.ok) {{
                    alert('Message sent successfully! We will get back to you soon.');
                    this.reset();
                }} else {{
                    alert('Failed to send message. Please try again.');
                }}
            }} catch (error) {{
                alert('Error sending message. Please try again.');
            }}
        }});

        // Newsletter form submission
        document.getElementById('newsletter-form').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {{
                business_owner_id: '{website_data["owner_id"]}',
                name: 'Newsletter Subscriber',
                email: formData.get('email'),
                registration_source: 'newsletter',
                website_id: '{website_data.get("_id", "")}'
            }};
            
            try {{
                const response = await fetch('/api/customers/register', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify(data)
                }});
                
                if (response.ok) {{
                    alert('Thank you for subscribing!');
                    this.reset();
                }} else {{
                    alert('Subscription failed. Please try again.');
                }}
            }} catch (error) {{
                alert('Error subscribing. Please try again.');
            }}
        }});

        // Track page visit
        fetch(`/api/website/{website_data.get("_id", "")}/visit`, {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify({{
                page: window.location.pathname,
                referrer: document.referrer
            }})
        }}).catch(console.error);
    </script>
</body>
</html>
        """
        
        return html_template
    
    def _get_theme_colors(self, theme_name):
        """Get color scheme for theme"""
        color_schemes = {
            'warm': {'primary': '#FF6B35', 'secondary': '#F7931E', 'background': '#FFF8F0'},
            'fresh': {'primary': '#4CAF50', 'secondary': '#8BC34A', 'background': '#F1F8E9'},
            'elegant': {'primary': '#6A0DAD', 'secondary': '#9932CC', 'background': '#FAF0FF'},
            'modern': {'primary': '#2196F3', 'secondary': '#03DAC6', 'background': '#F0F8FF'},
            'classic': {'primary': '#212121', 'secondary': '#757575', 'background': '#FAFAFA'},
        }
        return color_schemes.get(theme_name, color_schemes['modern'])
    
    def _generate_services_html(self, services):
        """Generate HTML for services section"""
        services_html = ""
        for service in services:
            services_html += f"""
                <div class="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                    <h3 class="text-xl font-bold mb-3" style="color: var(--primary-color);">{service['name']}</h3>
                    <p class="text-gray-600">{service['description']}</p>
                </div>
            """
        return services_html
    
    def _generate_products_html(self, products):
        """Generate HTML for products section"""
        if not products:
            return ""
            
        products_html = f"""
        <!-- Products Section -->
        <section id="products" class="section-padding bg-white">
            <div class="max-w-6xl mx-auto">
                <div class="text-center mb-12">
                    <h2 class="text-4xl font-bold mb-4" style="color: var(--primary-color);">Our Products</h2>
                </div>
                <div class="grid md:grid-cols-3 gap-8">
        """
        
        for product in products[:6]:  # Show max 6 products
            products_html += f"""
                <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                    <img src="{product.get('image', '/api/placeholder/300/200')}" alt="{product['name']}" class="w-full h-48 object-cover">
                    <div class="p-6">
                        <h3 class="text-xl font-bold mb-2">{product['name']}</h3>
                        <p class="text-gray-600 mb-4">{product['description'][:100]}...</p>
                        <div class="flex justify-between items-center">
                            <span class="text-2xl font-bold" style="color: var(--primary-color);">${product['price']}</span>
                            <button onclick="inquireProduct('{product['name']}')" class="btn-primary text-sm">Inquire</button>
                        </div>
                    </div>
                </div>
            """
        
        products_html += """
                </div>
            </div>
        </section>
        
        <script>
            function inquireProduct(productName) {
                const message = `Hi, I'm interested in ${productName}. Please provide more information.`;
                document.querySelector('textarea[name="message"]').value = message;
                document.querySelector('#contact').scrollIntoView({ behavior: 'smooth' });
            }
        </script>
        """
        
        return products_html
    
    def _generate_contact_info_html(self, contact_info):
        """Generate HTML for contact information"""
        contact_html = ""
        
        if contact_info.get('address'):
            contact_html += f"""
                <div class="flex items-start space-x-3">
                    <svg class="w-5 h-5 mt-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <div>
                        <p class="font-medium">Address</p>
                        <p class="text-gray-600">{contact_info['address']}</p>
                    </div>
                </div>
            """
        
        if contact_info.get('phone'):
            contact_html += f"""
                <div class="flex items-start space-x-3">
                    <svg class="w-5 h-5 mt-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                    </svg>
                    <div>
                        <p class="font-medium">Phone</p>
                        <p class="text-gray-600">{contact_info['phone']}</p>
                    </div>
                </div>
            """
        
        if contact_info.get('email'):
            contact_html += f"""
                <div class="flex items-start space-x-3">
                    <svg class="w-5 h-5 mt-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                    <div>
                        <p class="font-medium">Email</p>
                        <p class="text-gray-600">{contact_info['email']}</p>
                    </div>
                </div>
            """
        
        if contact_info.get('hours'):
            contact_html += f"""
                <div class="flex items-start space-x-3">
                    <svg class="w-5 h-5 mt-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <div>
                        <p class="font-medium">Hours</p>
                        <p class="text-gray-600">{contact_info['hours']}</p>
                    </div>
                </div>
            """
        
        return contact_html
