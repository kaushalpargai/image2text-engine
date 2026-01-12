"""
Quick test script to verify OCR service connectivity
Run this from your host machine or another container
"""
import requests
import sys

def test_connection(base_url="http://localhost:8005"):
    """Test connection to OCR service"""
    print(f"Testing connection to: {base_url}")
    print("-" * 60)
    
    try:
        # Test 1: Home page
        print("\n1. Testing home page...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   [OK] Home page accessible")
        else:
            print(f"   [FAIL] Failed with status: {response.status_code}")
            return False
        
        # Test 2: Results endpoint
        print("\n2. Testing results endpoint...")
        response = requests.get(f"{base_url}/results", timeout=5)
        if response.status_code == 200:
            print("   [OK] Results endpoint accessible")
            data = response.json()
            print(f"   Found {len(data.get('results', []))} existing results")
        else:
            print(f"   [FAIL] Failed with status: {response.status_code}")
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed! Service is accessible.")
        print("=" * 60)
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Connection Error: Cannot connect to {base_url}")
        print("  Make sure the Docker container is running.")
        return False
    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Timeout Error: Service took too long to respond")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    # Default to localhost, but can be changed for container-to-container
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8005"
    
    success = test_connection(url)
    sys.exit(0 if success else 1)
