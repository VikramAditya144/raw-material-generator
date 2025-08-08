import streamlit as st
import requests
import json
import time
from typing import List, Dict

# Configure the API key
GEMINI_API_KEY = "AIzaSyAqb4ZV4vCfhrfvinj_rGs3lZOP1--zyqc"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def call_gemini_api(prompt: str) -> str:
    """Call Gemini API using REST endpoint"""
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2048,
        }
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Error: No response generated"
            
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error processing response: {str(e)}")
        return None

def generate_raw_materials(product_name: str) -> Dict:
    """Generate raw materials and suppliers for a given product"""
    
    prompt = f"""
    Analyze the product "{product_name}" and provide a detailed breakdown of raw materials needed.
    
    Please respond with ONLY a valid JSON object in the following format:
    {{
        "product_analysis": {{
            "product_name": "{product_name}",
            "category": "product category",
            "manufacturing_complexity": "low/medium/high"
        }},
        "raw_materials": [
            {{
                "material_name": "material name",
                "quantity": "amount with unit",
                "quality_grade": "specification",
                "purpose": "what it's used for",
                "alternatives": ["alternative1", "alternative2"]
            }}
        ],
        "estimated_cost_range": "cost range in USD",
        "manufacturing_notes": "brief notes about the manufacturing process"
    }}
    
    Provide realistic and detailed information for manufacturing "{product_name}". Include all major raw materials needed.
    Make sure the response is valid JSON only, no additional text before or after.
    """
    
    response_text = call_gemini_api(prompt)
    
    if not response_text:
        return None
    
    try:
        # Clean the response text to extract JSON
        response_text = response_text.strip()
        
        # Find JSON boundaries
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        else:
            # If no JSON found, create a fallback response
            return create_fallback_response(product_name, response_text)
            
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON response: {str(e)}")
        return create_fallback_response(product_name, response_text)
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def create_fallback_response(product_name: str, raw_response: str) -> Dict:
    """Create a fallback response if JSON parsing fails"""
    return {
        "product_analysis": {
            "product_name": product_name,
            "category": "General Product",
            "manufacturing_complexity": "medium"
        },
        "raw_materials": [
            {
                "material_name": "Primary Material",
                "quantity": "To be determined",
                "quality_grade": "Standard grade",
                "purpose": "Main component",
                "alternatives": ["Alternative material 1", "Alternative material 2"]
            },
            {
                "material_name": "Secondary Material",
                "quantity": "To be determined",
                "quality_grade": "Commercial grade",
                "purpose": "Supporting component",
                "alternatives": ["Alternative material 3"]
            }
        ],
        "estimated_cost_range": "$100 - $500",
        "manufacturing_notes": f"Analysis generated for {product_name}. Please refine requirements based on specific needs."
    }

def get_dummy_suppliers(material_name: str) -> List[Dict]:
    """Generate dummy supplier recommendations"""
    # Clean material name for company generation
    clean_name = material_name.split()[0] if material_name else "Material"
    
    suppliers = [
        {
            "name": f"Global {clean_name} Industries",
            "location": "Mumbai, Maharashtra, India",
            "rating": 4.5,
            "price_range": "$$ - Moderate",
            "speciality": f"High-quality {material_name.lower()}",
            "contact": "+91-22-1234-5678",
            "email": f"sales@global{clean_name.lower()}.com",
            "minimum_order": "500 kg",
            "lead_time": "10-15 days"
        },
        {
            "name": f"{clean_name} Supply Co.",
            "location": "Delhi, India",
            "rating": 4.2,
            "price_range": "$ - Budget Friendly",
            "speciality": f"Bulk {material_name.lower()} supplier",
            "contact": "+91-11-9876-5432",
            "email": f"orders@{clean_name.lower()}supply.com",
            "minimum_order": "1000 kg",
            "lead_time": "7-12 days"
        },
        {
            "name": f"Premium {clean_name} Ltd.",
            "location": "Bangalore, Karnataka, India",
            "rating": 4.8,
            "price_range": "$$$ - Premium",
            "speciality": f"Certified high-grade {material_name.lower()}",
            "contact": "+91-80-5555-1234",
            "email": f"info@premium{clean_name.lower()}.in",
            "minimum_order": "250 kg",
            "lead_time": "15-20 days"
        }
    ]
    return suppliers[:2]  # Return 2 suppliers per material

def main():
    st.set_page_config(
        page_title="Raw Materials Generator",
        page_icon="",
        layout="wide"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    .supplier-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1> Raw Materials Generator</h1>
        <p>Powered by Google Gemini AI - Analyze products and get raw material requirements</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header(" How to Use")
    st.sidebar.markdown("""
    **Steps:**
    1. Enter the product name you want to analyze
    2. Optionally upload product images (for reference)
    3. Click 'Generate Raw Materials' to get AI analysis
    4. View detailed material requirements and supplier recommendations
    5. Export results for further use
    
    **Examples:**
    - Smartphone
    - Wooden Dining Table
    - Cotton T-shirt
    - Ceramic Mug
    - Leather Handbag
    """)
    
    # Test API Connection
    with st.sidebar:
        st.markdown("---")
        if st.button(" Test API Connection"):
            with st.spinner("Testing..."):
                test_response = call_gemini_api("Hello, respond with 'API Working'")
                if test_response:
                    st.success("API Connected Successfully!")
                else:
                    st.error(" API Connection Failed")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Product Information")
        
        # Product name input
        product_name = st.text_input(
            "Product Name *",
            placeholder="e.g., Smartphone, T-shirt, Wooden Chair, etc.",
            help="Enter the name of the product you want to analyze"
        )
        
        # Product description (optional)
        product_desc = st.text_area(
            "Product Description (Optional)",
            placeholder="Add any specific details about your product...",
            height=100
        )
        
        # Dummy image upload
        st.subheader("Product Images (Reference Only)")
        uploaded_files = st.file_uploader(
            "Upload product images",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Images are for reference only and won't be sent to the API"
        )
        
        if uploaded_files:
            st.success(f" {len(uploaded_files)} image(s) uploaded for reference")
            # Display thumbnails
            cols = st.columns(min(len(uploaded_files), 3))
            for i, file in enumerate(uploaded_files[:3]):
                with cols[i]:
                    st.image(file, caption=file.name, width=100)
    
    with col2:
        st.header(" Generate Analysis")
        
        # Analysis button
        analyze_button = st.button(
            "Generate Raw Materials Analysis", 
            type="primary", 
            use_container_width=True,
            disabled=not product_name.strip()
        )
        
        if not product_name.strip():
            st.warning(" Please enter a product name to continue")
        
        if analyze_button and product_name.strip():
            # Combine product name and description
            full_product_info = product_name
            if product_desc.strip():
                full_product_info += f" - {product_desc}"
            
            with st.spinner(" AI is analyzing your product..."):
                # Progress bar for better UX
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Connecting to Gemini AI...")
                progress_bar.progress(25)
                time.sleep(1)
                
                status_text.text("Analyzing product requirements...")
                progress_bar.progress(50)
                
                # Generate materials
                materials_data = generate_raw_materials(full_product_info)
                progress_bar.progress(75)
                
                status_text.text("Generating supplier recommendations...")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                status_text.empty()
                progress_bar.empty()
                
                if materials_data:
                    st.success("✅ Analysis completed successfully!")
                    
                    # Store in session state
                    st.session_state['materials_data'] = materials_data
                    st.session_state['product_name'] = product_name
                else:
                    st.error("Failed to generate analysis. Please try again.")
    
    # Display results if available
    if 'materials_data' in st.session_state:
        st.markdown("---")
        display_results(st.session_state['materials_data'], st.session_state['product_name'])

def display_results(materials_data: Dict, product_name: str):
    """Display the analysis results"""
    
    # Product Analysis Summary
    st.header("Product Analysis Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Product Category", 
            materials_data['product_analysis']['category'],
            help="Categorization of the product type"
        )
    with col2:
        st.metric(
            "Manufacturing Complexity", 
            materials_data['product_analysis']['manufacturing_complexity'].title(),
            help="Complexity level of manufacturing process"
        )
    with col3:
        st.metric(
            "Estimated Cost Range", 
            materials_data['estimated_cost_range'],
            help="Estimated cost range for raw materials"
        )
    
    # Manufacturing Notes
    if 'manufacturing_notes' in materials_data:
        st.info(f" **Manufacturing Notes:** {materials_data['manufacturing_notes']}")
    
    # Raw Materials Section
    st.header("Required Raw Materials")
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs([" Materials List", "Suppliers Directory"])
    
    with tab1:
        for i, material in enumerate(materials_data['raw_materials']):
            with st.expander(f" {material['material_name']}", expanded=i < 3):
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown(f"** Quantity Required:** {material['quantity']}")
                    st.markdown(f"** Quality Grade:** {material['quality_grade']}")
                    st.markdown(f"** Purpose:** {material['purpose']}")
                    
                    if material.get('alternatives'):
                        alternatives = ', '.join(material['alternatives'])
                        st.markdown(f"** Alternatives:** {alternatives}")
                
                with col2:
                    st.markdown("** Material Info:**")
                    # Create a simple info box
                    st.markdown(f"""
                    <div style="background: #f0f2f6; padding: 1rem; border-radius: 5px; margin: 0.5rem 0;">
                        <strong>Material #{i+1}</strong><br>
                        Priority: {"High" if i < 2 else "Medium"}<br>
                        Type: {"Primary" if i < 2 else "Secondary"}
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Recommended Suppliers by Material")
        
        for i, material in enumerate(materials_data['raw_materials']):
            st.subheader(f" {material['material_name']}")
            
            suppliers = get_dummy_suppliers(material['material_name'])
            
            cols = st.columns(len(suppliers))
            for j, supplier in enumerate(suppliers):
                with cols[j]:
                    st.markdown(f"""
                    <div class="supplier-card">
                        <h4>{supplier['name']}</h4>
                        <p><strong> Location:</strong> {supplier['location']}</p>
                        <p><strong> Rating:</strong> {supplier['rating']}/5.0</p>
                        <p><strong> Pricing:</strong> {supplier['price_range']}</p>
                        <p><strong> Specialty:</strong> {supplier['speciality']}</p>
                        <p><strong> Contact:</strong> {supplier['contact']}</p>
                        <p><strong> Email:</strong> {supplier['email']}</p>
                        <p><strong> Min Order:</strong> {supplier['minimum_order']}</p>
                        <p><strong> Lead Time:</strong> {supplier['lead_time']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Export functionality
    st.header("📁 Export & Save Results")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download as JSON
        json_data = json.dumps(materials_data, indent=2)
        st.download_button(
            label=" Download JSON",
            data=json_data,
            file_name=f"{product_name.lower().replace(' ', '_')}_analysis.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Download as formatted text
        export_text = create_export_text(materials_data, product_name)
        st.download_button(
            label=" Download Report",
            data=export_text,
            file_name=f"{product_name.lower().replace(' ', '_')}_report.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        if st.button("Generate New Analysis", use_container_width=True):
            # Clear session state to start fresh
            if 'materials_data' in st.session_state:
                del st.session_state['materials_data']
            if 'product_name' in st.session_state:
                del st.session_state['product_name']
            st.rerun()

def create_export_text(materials_data: Dict, product_name: str) -> str:
    """Create formatted text for export"""
    text = f"RAW MATERIALS ANALYSIS REPORT\n"
    text += f"Product: {product_name}\n"
    text += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += "=" * 60 + "\n\n"
    
    text += f"PRODUCT ANALYSIS:\n"
    text += f"Category: {materials_data['product_analysis']['category']}\n"
    text += f"Manufacturing Complexity: {materials_data['product_analysis']['manufacturing_complexity']}\n"
    text += f"Estimated Cost Range: {materials_data['estimated_cost_range']}\n\n"
    
    if 'manufacturing_notes' in materials_data:
        text += f"Manufacturing Notes: {materials_data['manufacturing_notes']}\n\n"
    
    text += "RAW MATERIALS REQUIRED:\n"
    text += "-" * 40 + "\n"
    
    for i, material in enumerate(materials_data['raw_materials'], 1):
        text += f"\n{i}. {material['material_name']}\n"
        text += f"   Quantity: {material['quantity']}\n"
        text += f"   Quality Grade: {material['quality_grade']}\n"
        text += f"   Purpose: {material['purpose']}\n"
        if material.get('alternatives'):
            text += f"   Alternatives: {', '.join(material['alternatives'])}\n"
        
        # Add suppliers
        suppliers = get_dummy_suppliers(material['material_name'])
        text += f"   \n   RECOMMENDED SUPPLIERS:\n"
        for j, supplier in enumerate(suppliers, 1):
            text += f"   {j}. {supplier['name']}\n"
            text += f"      Location: {supplier['location']}\n"
            text += f"      Rating: {supplier['rating']}/5.0\n"
            text += f"      Contact: {supplier['contact']}\n"
            text += f"      Min Order: {supplier['minimum_order']}\n"
            text += f"      Lead Time: {supplier['lead_time']}\n"
        text += "\n"
    
    text += "\n" + "=" * 60 + "\n"
    text += "Report generated by Raw Materials Generator - Powered by Google Gemini AI\n"
    
    return text

if __name__ == "__main__":
    main()