"""Customer service for property search and advice functionality."""
import json
import requests
from datetime import datetime
from app.models import CustomerEnquiry, LLMConfig


class CustomerService:
    """Service class for customer property operations."""
    
    @staticmethod
    def search_properties(search_criteria):
        """Search properties using web search (placeholder implementation)."""
        # This is a placeholder implementation
        # In a real application, you would integrate with property APIs like 99acres
        
        location = search_criteria.get('location', '')
        property_type = search_criteria.get('property_type', '')
        budget_min = search_criteria.get('budget_min', 0)
        budget_max = search_criteria.get('budget_max', 0)
        
        # Mock property results
        mock_results = [
            {
                'id': 1,
                'title': f'Beautiful {property_type} in {location}',
                'location': location,
                'price': budget_min + 500000 if budget_min else 5000000,
                'area': '1200 sq ft',
                'bedrooms': 2 if property_type == '2BHK' else 3,
                'bathrooms': 2,
                'description': f'Spacious {property_type} apartment with modern amenities',
                'image_url': 'https://via.placeholder.com/300x200',
                'contact': '+91-9876543210'
            },
            {
                'id': 2,
                'title': f'Premium {property_type} in {location}',
                'location': location,
                'price': budget_max - 200000 if budget_max else 7500000,
                'area': '1500 sq ft',
                'bedrooms': 3 if property_type == '3BHK' else 2,
                'bathrooms': 3,
                'description': f'Luxury {property_type} with premium finishes',
                'image_url': 'https://via.placeholder.com/300x200',
                'contact': '+91-9876543211'
            }
        ]
        
        return mock_results
    
    @staticmethod
    def get_property_advice(advice_request):
        """Get property advice using LLM."""
        # Get active LLM configuration
        llm_config = LLMConfig.get_active_config()
        
        if not llm_config:
            return "LLM configuration not found. Please contact administrator."
        
        try:
            # This is a placeholder implementation
            # In a real application, you would call OpenAI API or other LLM service
            
            # Mock LLM response based on request
            if 'investment' in advice_request.lower():
                advice = """Based on your investment query, here are some key recommendations:

1. **Location Analysis**: Focus on areas with upcoming infrastructure development like metro connectivity, IT hubs, and educational institutions.

2. **Property Type**: For investment purposes, 2BHK and 3BHK apartments typically offer better rental yields and resale value.

3. **Budget Allocation**: Consider allocating 70-80% of your budget to the property cost and keep 20-30% for registration, taxes, and furnishing.

4. **Market Timing**: Current market conditions suggest it's a good time for investment with stable prices and low interest rates.

5. **Legal Verification**: Always verify RERA registration, clear title, and approved building plans before investing.

6. **Rental Potential**: Properties near IT corridors, hospitals, and educational institutions typically have higher rental demand.

Would you like specific recommendations for any particular location or budget range?"""
            
            elif 'first home' in advice_request.lower() or 'buying' in advice_request.lower():
                advice = """Congratulations on planning to buy your first home! Here's comprehensive guidance:

1. **Financial Planning**: 
   - Ensure your EMI doesn't exceed 40% of your monthly income
   - Keep 20-25% ready for down payment
   - Budget for additional costs (registration, stamp duty, legal fees)

2. **Location Priorities**:
   - Proximity to workplace (consider commute time and cost)
   - Access to schools, hospitals, and shopping centers
   - Public transportation connectivity

3. **Property Checklist**:
   - RERA registered projects
   - Clear title and approved building plans
   - Quality of construction and amenities
   - Possession timeline and builder reputation

4. **Home Loan Tips**:
   - Compare interest rates from multiple banks
   - Check for pre-approved loan offers
   - Consider floating vs fixed rate options

5. **Future Considerations**:
   - Resale value potential
   - Rental income possibility
   - Infrastructure development plans in the area

Feel free to share your specific requirements for personalized advice!"""
            
            else:
                advice = f"""Thank you for your property inquiry. Based on your request: "{advice_request}"

Here are some general recommendations:

1. **Market Research**: Always research the local property market trends, average prices, and growth potential in your target area.

2. **Legal Due Diligence**: Verify all legal documents, RERA registration, and clear title before making any decision.

3. **Financial Planning**: Ensure you have adequate funds not just for the property cost but also for registration, taxes, and maintenance.

4. **Location Analysis**: Consider factors like connectivity, infrastructure development, social amenities, and future growth prospects.

5. **Professional Consultation**: Consider consulting with local real estate experts, legal advisors, and financial planners.

For more specific advice, please provide details about your budget, preferred location, property type, and purpose (investment/residence).

Would you like me to elaborate on any of these points?"""
            
            return advice
            
        except Exception as e:
            return f"Error generating advice: {str(e)}. Please try again or contact support."
    
    @staticmethod
    def generate_report(customer_id, enquiry_ids):
        """Generate comprehensive property report."""
        try:
            # Get customer enquiries
            enquiries = CustomerEnquiry.query.filter(
                CustomerEnquiry.customer_id == customer_id,
                CustomerEnquiry.id.in_(enquiry_ids)
            ).all()
            
            if not enquiries:
                return "No enquiries found for report generation."
            
            # Generate report content
            report = f"""
PROPERTY SEARCH & ADVISORY REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Customer ID: {customer_id}

=== SUMMARY ===
Total Enquiries: {len(enquiries)}
Search Requests: {len([e for e in enquiries if e.enquiry_type == 'search'])}
Advice Requests: {len([e for e in enquiries if e.enquiry_type == 'advice'])}

=== DETAILED ENQUIRIES ===
"""
            
            for i, enquiry in enumerate(enquiries, 1):
                report += f"\n{i}. ENQUIRY #{enquiry.id} ({enquiry.enquiry_type.upper()})\n"
                report += f"   Date: {enquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                if enquiry.enquiry_type == 'search':
                    if enquiry.search_criteria:
                        criteria = json.loads(enquiry.search_criteria)
                        report += f"   Search Criteria: {criteria}\n"
                
                elif enquiry.enquiry_type == 'advice':
                    if enquiry.advice_request:
                        report += f"   Request: {enquiry.advice_request[:100]}...\n"
                    if enquiry.llm_response:
                        report += f"   Advice: {enquiry.llm_response[:200]}...\n"
                
                report += "\n"
            
            report += """
=== RECOMMENDATIONS ===
Based on your enquiries, here are our key recommendations:

1. Continue researching properties in your preferred locations
2. Consider consulting with our real estate experts for personalized guidance
3. Keep track of market trends and price movements
4. Ensure all legal verifications before making any purchase decisions
5. Plan your finances including additional costs beyond property price

For further assistance, please contact our support team.

---
This report is generated automatically based on your enquiry history.
For detailed consultation, please schedule an appointment with our experts.
"""
            
            return report
            
        except Exception as e:
            return f"Error generating report: {str(e)}"