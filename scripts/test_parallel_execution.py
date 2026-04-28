"""Test script for parallel execution performance."""
import requests
import time
import json

API_URL = "http://localhost:8000"

# Test SQL schema
TEST_SQL = """
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url VARCHAR(500),
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled'),
    total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    parent_id INT,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);
"""


def test_health():
    """Test API health check."""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"   AI Provider: {data['ai_provider']}")
            print(f"   AI Available: {data['ai_available']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_parallel_conversion():
    """Test parallel conversion performance."""
    print("\n🚀 Testing parallel conversion...")
    print(f"   SQL: {len(TEST_SQL)} characters, {len(TEST_SQL.split('CREATE TABLE'))-1} tables")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/api/convert",
            json={
                "sql": TEST_SQL,
                "target_databases": ["mongodb", "cassandra", "neo4j"],
                "input_method": "manual",
                "include_ai_explanation": True
            },
            timeout=60
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversion completed in {duration:.2f}s")
            
            # Check results
            databases = []
            if data.get('mongodb'):
                databases.append('MongoDB')
                print(f"   ✓ MongoDB: {len(data['mongodb']['schema'])} chars, score: {data['mongodb']['score']}")
            
            if data.get('cassandra'):
                databases.append('Cassandra')
                print(f"   ✓ Cassandra: {len(data['cassandra']['schema'])} chars, score: {data['cassandra']['score']}")
            
            if data.get('neo4j'):
                databases.append('Neo4j')
                print(f"   ✓ Neo4j: {len(data['neo4j']['schema'])} chars, score: {data['neo4j']['score']}")
            
            print(f"\n📊 Performance Metrics:")
            print(f"   Total Time: {duration:.2f}s")
            print(f"   Databases: {len(databases)}")
            print(f"   Avg per DB: {duration/len(databases):.2f}s")
            print(f"   Parallel Efficiency: {(len(databases) * 5) / duration:.1f}x")
            
            # Check metadata
            if data.get('metadata'):
                meta = data['metadata']
                print(f"\n📋 Metadata:")
                print(f"   Tables: {meta.get('table_count', 'N/A')}")
                print(f"   Relationships: {meta.get('relationship_count', 'N/A')}")
                print(f"   Parallel Execution: {meta.get('parallel_execution', False)}")
            
            return True
        else:
            print(f"❌ Conversion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 60s")
        return False
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return False


def test_sequential_vs_parallel():
    """Compare sequential vs parallel execution times."""
    print("\n⚖️  Comparing Sequential vs Parallel...")
    
    # Test single database (sequential baseline)
    print("\n1️⃣  Testing single database (MongoDB only)...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/convert",
            json={
                "sql": TEST_SQL,
                "target_databases": ["mongodb"],
                "input_method": "manual",
                "include_ai_explanation": True
            },
            timeout=30
        )
        single_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Single DB: {single_time:.2f}s")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            single_time = None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        single_time = None
    
    # Test all databases (parallel)
    print("\n3️⃣  Testing all databases (parallel)...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/convert",
            json={
                "sql": TEST_SQL,
                "target_databases": ["mongodb", "cassandra", "neo4j"],
                "input_method": "manual",
                "include_ai_explanation": True
            },
            timeout=60
        )
        parallel_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Parallel (3 DBs): {parallel_time:.2f}s")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            parallel_time = None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        parallel_time = None
    
    # Calculate speedup
    if single_time and parallel_time:
        expected_sequential = single_time * 3
        speedup = expected_sequential / parallel_time
        efficiency = (speedup / 3) * 100
        
        print(f"\n📈 Performance Analysis:")
        print(f"   Single DB Time: {single_time:.2f}s")
        print(f"   Expected Sequential (3 DBs): {expected_sequential:.2f}s")
        print(f"   Actual Parallel (3 DBs): {parallel_time:.2f}s")
        print(f"   Speedup: {speedup:.2f}x")
        print(f"   Parallel Efficiency: {efficiency:.1f}%")
        print(f"   Time Saved: {expected_sequential - parallel_time:.2f}s ({((expected_sequential - parallel_time) / expected_sequential * 100):.1f}%)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Parallel Execution Performance Test")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ API is not available. Please start the backend server.")
        print("   Run: cd backend && python -m uvicorn main:app --reload")
        return
    
    # Test 2: Parallel conversion
    test_parallel_conversion()
    
    # Test 3: Sequential vs Parallel comparison
    test_sequential_vs_parallel()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
