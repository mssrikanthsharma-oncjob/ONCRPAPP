#!/usr/bin/env python3
"""
Simple test script to verify customer functionality
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_customer_login():
    """Test customer login"""
    print("Testing customer login...")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "customer",
        "password": "customer123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Customer login successful")
        print(f"User role: {data['data']['user']['role']}")
        return data['data']['token']
    else:
        print(f"❌ Customer login failed: {response.text}")
        return None

def test_send_otp(token):
    """Test sending OTP"""
    print("\nTesting OTP sending...")
    
    response = requests.post(f"{BASE_URL}/api/customer/send-otp", 
        json={"email": "test@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ OTP sent successfully")
        print(f"Demo OTP: {data.get('otp', 'Not provided')}")
        return data.get('otp')
    else:
        print(f"❌ OTP sending failed: {response.text}")
        return None

def test_verify_otp(token, otp):
    """Test OTP verification"""
    print("\nTesting OTP verification...")
    
    response = requests.post(f"{BASE_URL}/api/customer/verify-otp", 
        json={"otp_code": otp},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print("✅ OTP verification successful")
        return True
    else:
        print(f"❌ OTP verification failed: {response.text}")
        return False

def test_property_search(token):
    """Test property search"""
    print("\nTesting property search...")
    
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
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Property search successful")
        print(f"Found {len(data['results'])} properties")
        return data['enquiry_id']
    else:
        print(f"❌ Property search failed: {response.text}")
        return None

def test_property_advice(token):
    """Test property advice"""
    print("\nTesting property advice...")
    
    response = requests.post(f"{BASE_URL}/api/customer/get-property-advice", 
        json={
            "advice_request": "I'm looking to buy my first home in Mumbai with a budget of 80 lakhs. What should I consider?"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Property advice successful")
        print(f"Advice preview: {data['advice'][:100]}...")
        return data['enquiry_id']
    else:
        print(f"❌ Property advice failed: {response.text}")
        return None

def test_admin_enquiries(admin_token):
    """Test admin viewing customer enquiries"""
    print("\nTesting admin enquiry viewing...")
    
    response = requests.get(f"{BASE_URL}/api/admin/customer-enquiries",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Admin can view customer enquiries")
        print(f"Total enquiries: {len(data['enquiries'])}")
        return True
    else:
        print(f"❌ Admin enquiry viewing failed: {response.text}")
        return False

def get_admin_token():
    """Get admin token for testing"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        return response.json()['data']['token']
    return None

def main():
    print("🚀 Testing Customer Functionality")
    print("=" * 50)
    
    # Test customer login
    customer_token = test_customer_login()
    if not customer_token:
        return
    
    # Test OTP flow
    otp = test_send_otp(customer_token)
    if not otp:
        return
    
    if not test_verify_otp(customer_token, otp):
        return
    
    # Test property search
    search_enquiry_id = test_property_search(customer_token)
    
    # Test property advice
    advice_enquiry_id = test_property_advice(customer_token)
    
    # Test admin functionality
    admin_token = get_admin_token()
    if admin_token:
        test_admin_enquiries(admin_token)
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()