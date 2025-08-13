#!/usr/bin/env python3
"""
Test Coordinate Integration in Matching Algorithm
Verifies that the enhanced matching system uses coordinates correctly
"""

import sys
sys.path.append('.')
from main import normalize_city, get_city_coordinates, calculate_distance_km, calculate_location_priority

def test_coordinate_integration():
    """Test coordinate integration in the matching algorithm"""
    
    print("🔗 Testing Coordinate Integration in Matching Algorithm")
    print("="*55)
    
    # Test users from different CIS cities
    test_users = [
        {
            'user_id': 1001,
            'name': 'Алексей',
            'city': 'Москва',
            'latitude': None,
            'longitude': None,
        },
        {
            'user_id': 1002,
            'name': 'Мария',
            'city': 'Санкт-Петербург',
            'latitude': None,
            'longitude': None,
        },
        {
            'user_id': 1003,
            'name': 'Dmitry',
            'city': 'Almaty',
            'latitude': None,
            'longitude': None,
        },
        {
            'user_id': 1004,
            'name': 'Анна',
            'city': 'Минск',
            'latitude': None,
            'longitude': None,
        },
        {
            'user_id': 1005,
            'name': 'Нурбек',
            'city': 'Бишкек',
            'latitude': None,
            'longitude': None,
        },
        {
            'user_id': 1006,
            'name': 'Elena',
            'city': 'Kiev',
            'latitude': None,
            'longitude': None,
        },
        {
            'user_id': 1007,
            'name': 'Александр',
            'city': 'мск',  # Test abbreviation
            'latitude': None,
            'longitude': None,
        },
        {
            'user_id': 1008,
            'name': 'Ольга',
            'city': 'СПб',  # Test abbreviation
            'latitude': None,
            'longitude': None,
        },
    ]
    
    print(f"Testing {len(test_users)} users from different CIS cities...\n")
    
    # Test coordinate resolution for each user
    print("📍 City Coordinate Resolution:")
    print("-" * 30)
    
    for user in test_users:
        city = user['city']
        coords = get_city_coordinates(city)
        normalized = normalize_city(city)
        
        if coords:
            lat, lon = coords
            print(f"✅ {user['name']}: '{city}' → '{normalized}' → ({lat:.4f}, {lon:.4f})")
        else:
            print(f"❌ {user['name']}: '{city}' → '{normalized}' → No coordinates")
    
    # Test location priority calculations
    print(f"\n🎯 Location Priority Testing:")
    print("-" * 30)
    
    moscow_user = test_users[0]  # Москва
    
    # Test different distance scenarios
    test_pairs = [
        (moscow_user, test_users[1], "Moscow → St. Petersburg (same country)"),
        (moscow_user, test_users[2], "Moscow → Almaty (different country)"),
        (moscow_user, test_users[3], "Moscow → Minsk (neighboring country)"),
        (moscow_user, test_users[4], "Moscow → Bishkek (far CIS)"),
        (moscow_user, test_users[5], "Moscow → Kiev (neighboring country)"),
        (moscow_user, test_users[6], "Moscow → Moscow abbreviation (same city)"),
        (test_users[1], test_users[7], "St. Petersburg → SPb abbreviation (same city)"),
    ]
    
    for user1, user2, description in test_pairs:
        priority = calculate_location_priority(user1, user2)
        
        # Get actual distance for reference
        coords1 = get_city_coordinates(user1['city'])
        coords2 = get_city_coordinates(user2['city'])
        
        if coords1 and coords2:
            lat1, lon1 = coords1
            lat2, lon2 = coords2
            distance = calculate_distance_km(lat1, lon1, lat2, lon2)
            print(f"Priority {priority}: {description} ({distance:.0f}km)")
        else:
            print(f"Priority {priority}: {description} (coordinates missing)")
    
    # Test coordinate accuracy with known distances
    print(f"\n📏 Distance Accuracy Verification:")
    print("-" * 30)
    
    known_distances = [
        ("Москва", "Санкт-Петербург", 635, "Historical capitals"),
        ("Москва", "Киев", 755, "Major eastern European cities"),
        ("Алматы", "Бишкек", 213, "Central Asian neighbors"),
        ("Минск", "Киев", 465, "Eastern European capitals"),
        ("Ташкент", "Алматы", 472, "Central Asian hubs"),
    ]
    
    accuracy_count = 0
    total_distance_tests = len(known_distances)
    
    for city1, city2, expected_km, description in known_distances:
        coords1 = get_city_coordinates(city1)
        coords2 = get_city_coordinates(city2)
        
        if coords1 and coords2:
            lat1, lon1 = coords1
            lat2, lon2 = coords2
            calculated_km = calculate_distance_km(lat1, lon1, lat2, lon2)
            
            # Allow 15% tolerance for geographical distance calculations
            tolerance = expected_km * 0.15
            if abs(calculated_km - expected_km) <= tolerance:
                accuracy_count += 1
                print(f"✅ {city1} ↔ {city2}: {calculated_km:.0f}km (expected ~{expected_km}km) - {description}")
            else:
                print(f"⚠️  {city1} ↔ {city2}: {calculated_km:.0f}km (expected ~{expected_km}km) - {description}")
        else:
            print(f"❌ {city1} ↔ {city2}: Missing coordinates - {description}")
    
    # Summary
    print(f"\n" + "="*55)
    print(f"🎯 Coordinate Integration Test Summary")
    print(f"Distance Accuracy: {accuracy_count}/{total_distance_tests} ({(accuracy_count/total_distance_tests)*100:.1f}%)")
    
    if accuracy_count >= total_distance_tests * 0.8:
        print("🎉 Excellent coordinate integration! Matching will be highly accurate.")
        return True
    elif accuracy_count >= total_distance_tests * 0.6:
        print("✅ Good coordinate integration! Most matches will be accurate.")
        return True
    else:
        print("⚠️  Some coordinate integration issues found. Review distance calculations.")
        return False

if __name__ == "__main__":
    test_coordinate_integration()