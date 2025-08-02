"""
Debug script to test template loading
"""
import os
import sys

# Add backend to path
backend_path = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\backend"
sys.path.append(backend_path)

def test_template_path():
    print("=== Template Path Debug ===")
    
    # Simulate the path resolution from netlify_service.py
    # This is what __file__ would be in the actual service
    mock_file = r"C:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\backend\app\services\netlify_service.py"
    
    print(f"Mock __file__: {mock_file}")
    
    # This is the path calculation from the service
    calculated_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(mock_file))),
        'netlify-functions',
        'enhanced-mini-website-template.html'
    )
    
    print(f"Calculated path: {calculated_path}")
    print(f"Path exists: {os.path.exists(calculated_path)}")
    
    # Let's see each step
    step1 = os.path.dirname(mock_file)  # backend/app/services
    step2 = os.path.dirname(step1)      # backend/app
    step3 = os.path.dirname(step2)      # backend
    step4 = os.path.dirname(step3)      # break-even
    
    print(f"Step 1 (dirname of file): {step1}")
    print(f"Step 2 (dirname of step1): {step2}")
    print(f"Step 3 (dirname of step2): {step3}")
    print(f"Step 4 (dirname of step3): {step4}")
    
    final_path = os.path.join(step4, 'netlify-functions', 'enhanced-mini-website-template.html')
    print(f"Final path: {final_path}")
    print(f"Final path exists: {os.path.exists(final_path)}")
    
    # Test if template has the required content
    if os.path.exists(final_path):
        with open(final_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Template size: {len(content)} characters")
            print(f"Has nav-tabs: {'nav-tabs' in content}")
            print(f"Has feedbackForm: {'feedbackForm' in content}")
            print(f"Has registration: {'register-user' in content}")
            
            # Check if it's the right template by looking for unique enhanced features
            has_enhanced_features = all([
                'nav-tabs' in content,
                'feedbackForm' in content,
                'customerLoginForm' in content,
                'Customer Login' in content,
                'Stay Connected' in content
            ])
            print(f"Has all enhanced features: {has_enhanced_features}")
    else:
        print("❌ Template file not found!")

if __name__ == "__main__":
    test_template_path()
