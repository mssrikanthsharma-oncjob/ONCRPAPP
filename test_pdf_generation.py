#!/usr/bin/env python3
"""
Test script for PDF generation functionality
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_customer_workflow():
    """Test complete customer workflow with PDF generation"""
    print("🧪 Testing Customer PDF Generation Workflow")
    print("=" * 60)
    
    # 1. Customer login
    print("1. Customer login...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "customer",
        "password": "customer123"
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token = response.json()['data']['token']
    print("✅ Customer login successful")
    
    # 2. Property search
    print("\n2. Property search...")
    response = requests.post(f"{BASE_URL}/api/customer/search-properties", 
        json={
            "search_criteria": {
                "location": "Mumbai",
                "property_type": "2BHK",
                "budget_min": 5000000,
                "budget_max": 10000000
            }
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Property search failed: {response.text}")
        return
    
    search_data = response.json()
    print(f"✅ Property search successful - Found {len(search_data['results'])} properties")
    
    # 3. Property advice
    print("\n3. Property advice...")
    response = requests.post(f"{BASE_URL}/api/customer/get-property-advice", 
        json={
            "advice_request": "I'm looking to buy my first home in Mumbai with a budget of 80 lakhs. What should I consider?"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Property advice failed: {response.text}")
        return
    
    advice_data = response.json()
    print("✅ Property advice successful")
    
    # 4. Send OTP
    print("\n4. Send OTP for email verification...")
    response = requests.post(f"{BASE_URL}/api/customer/send-otp", 
        json={"email": "test@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ OTP sending failed: {response.text}")
        return
    
    otp_data = response.json()
    otp_code = otp_data.get('otp')
    print(f"✅ OTP sent successfully - Demo OTP: {otp_code}")
    
    # 5. Verify OTP
    print("\n5. Verify OTP...")
    response = requests.post(f"{BASE_URL}/api/customer/verify-otp", 
        json={"otp_code": otp_code},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ OTP verification failed: {response.text}")
        return
    
    print("✅ OTP verification successful")
    
    # 6. Get activity summary
    print("\n6. Get activity summary...")
    response = requests.get(f"{BASE_URL}/api/customer/get-activity-summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Activity summary failed: {response.text}")
        return
    
    activity_data = response.json()
    print(f"✅ Activity summary: {activity_data['total_enquiries']} total enquiries")
    
    # 7. Generate PDF report
    print("\n7. Generate PDF report...")
    response = requests.post(f"{BASE_URL}/api/customer/generate-pdf-report", 
        json={
            "report_type": "comprehensive",
            "enquiry_ids": []
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ PDF generation failed: {response.text}")
        return
    
    # Save PDF file
    with open("test_report.pdf", "wb") as f:
        f.write(response.content)
    
    print("✅ PDF report generated successfully - Saved as 'test_report.pdf'")
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed successfully!")
    print("📄 Check 'test_report.pdf' for the generated report")

if __name__ == "__main__":
    test_customer_workflow()