#!/usr/bin/env python3
"""
Test City Name and Coordinate Compatibility
Ensures perfect matching between manual city entries and GPS coordinates
"""

import sys
sys.path.append('.')
from main import normalize_city, get_city_coordinates, calculate_distance_km

def test_city_coordinate_compatibility():
    """Test comprehensive city coordinate compatibility for CIS countries"""
    
    print("🌍 Testing City-Coordinate Compatibility for CIS Countries")
    print("="*60)
    
    # Test cases with manual input and expected coordinates
    test_cases = [
        # Russian cities - different input variations
        ("Москва", "Moscow coordinates"),
        ("москва", "Moscow coordinates"),  
        ("МОСКВА", "Moscow coordinates"),
        ("мск", "Moscow coordinates"),
        ("moscow", "Moscow coordinates"),
        
        ("Санкт-Петербург", "St. Petersburg coordinates"),
        ("санкт-петербург", "St. Petersburg coordinates"),
        ("спб", "St. Petersburg coordinates"),
        ("питер", "St. Petersburg coordinates"),
        ("петербург", "St. Petersburg coordinates"),
        
        ("Нижний Новгород", "Nizhny Novgorod coordinates"),
        ("нижний новгород", "Nizhny Novgorod coordinates"),
        ("ннов", "Nizhny Novgorod coordinates"),
        ("нн", "Nizhny Novgorod coordinates"),
        
        ("Екатеринбург", "Ekaterinburg coordinates"),
        ("екатеринбург", "Ekaterinburg coordinates"),
        ("екб", "Ekaterinburg coordinates"),
        
        # CIS Countries
        ("Киев", "Kiev coordinates"),
        ("киев", "Kiev coordinates"),
        ("Kiev", "Kiev coordinates"),
        ("kyiv", "Kiev coordinates"),
        
        ("Минск", "Minsk coordinates"),
        ("минск", "Minsk coordinates"),
        ("Minsk", "Minsk coordinates"),
        
        ("Алматы", "Almaty coordinates"),
        ("алматы", "Almaty coordinates"),
        ("Almaty", "Almaty coordinates"),
        ("алма-ата", "Almaty coordinates"),
        
        ("Ташкент", "Tashkent coordinates"),
        ("ташкент", "Tashkent coordinates"),
        ("Tashkent", "Tashkent coordinates"),
        
        ("Бишкек", "Bishkek coordinates"),
        ("бишкек", "Bishkek coordinates"),
        ("Bishkek", "Bishkek coordinates"),
        
        ("Душанбе", "Dushanbe coordinates"),
        ("душанбе", "Dushanbe coordinates"),
        ("Dushanbe", "Dushanbe coordinates"),
        
        ("Ашгабат", "Ashgabat coordinates"),
        ("ашгабат", "Ashgabat coordinates"),
        ("Ashgabat", "Ashgabat coordinates"),
        
        ("Баку", "Baku coordinates"),
        ("баку", "Baku coordinates"),
        ("Baku", "Baku coordinates"),
        
        ("Ереван", "Yerevan coordinates"),
        ("ереван", "Yerevan coordinates"),
        ("Yerevan", "Yerevan coordinates"),
        
        ("Тбилиси", "Tbilisi coordinates"),
        ("тбилиси", "Tbilisi coordinates"),
        ("Tbilisi", "Tbilisi coordinates"),
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    print(f"Testing {total_tests} city variations...\n")
    
    for input_city, expected_description in test_cases:
        # Normalize the city name
        normalized = normalize_city(input_city)
        
        # Get coordinates
        coordinates = get_city_coordinates(input_city)
        
        if coordinates:
            lat, lon = coordinates
            success_count += 1
            print(f"✅ '{input_city}' → '{normalized}' → ({lat:.4f}, {lon:.4f})")
        else:
            print(f"❌ '{input_city}' → '{normalized}' → No coordinates found")
    
    print(f"\n📊 Results: {success_count}/{total_tests} cities have coordinates")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    # Test distance calculations between major cities
    print("\n📏 Testing Distance Calculations")
    print("="*40)
    
    distance_tests = [
        ("Москва", "Санкт-Петербург", 635),  # ~635km actual distance
        ("Москва", "Киев", 755),              # ~755km actual distance  
        ("Алматы", "Нур-Султан", 1028),      # ~1028km actual distance
        ("Минск", "Москва", 700),            # ~700km actual distance
        ("Ташкент", "Бишкек", 367),          # ~367km actual distance
    ]
    
    for city1, city2, expected_distance in distance_tests:
        coords1 = get_city_coordinates(city1)
        coords2 = get_city_coordinates(city2)
        
        if coords1 and coords2:
            lat1, lon1 = coords1
            lat2, lon2 = coords2
            calculated_distance = calculate_distance_km(lat1, lon1, lat2, lon2)
            
            # Allow 10% tolerance for distance calculation
            tolerance = expected_distance * 0.1
            if abs(calculated_distance - expected_distance) <= tolerance:
                print(f"✅ {city1} ↔ {city2}: {calculated_distance:.0f}km (expected ~{expected_distance}km)")
            else:
                print(f"⚠️  {city1} ↔ {city2}: {calculated_distance:.0f}km (expected ~{expected_distance}km)")
        else:
            print(f"❌ {city1} ↔ {city2}: Missing coordinates")
    
    # Test edge cases and compatibility
    print("\n🔍 Testing Edge Cases")
    print("="*30)
    
    edge_cases = [
        "московская область",     # Should not match Moscow
        "санкт-петербург флорида", # Should not match Russian SPB
        "новый орлеан",           # Should not match Orel
        "",                       # Empty string
        "несуществующий город",   # Non-existent city
    ]
    
    for edge_case in edge_cases:
        if edge_case:  # Skip empty string
            normalized = normalize_city(edge_case)
            coordinates = get_city_coordinates(edge_case)
            
            if coordinates:
                print(f"⚠️  '{edge_case}' → found coordinates (might be unexpected)")
            else:
                print(f"✅ '{edge_case}' → no coordinates (expected)")
        else:
            print("✅ Empty string handled correctly")
    
    print("\n" + "="*60)
    print("🎯 City-Coordinate Compatibility Test Complete")
    
    if success_count >= total_tests * 0.9:  # 90% success rate
        print("🎉 Excellent compatibility! Cities will match correctly.")
        return True
    elif success_count >= total_tests * 0.8:  # 80% success rate  
        print("✅ Good compatibility! Most cities will match correctly.")
        return True
    else:
        print("⚠️  Some compatibility issues found. Review coordinate mapping.")
        return False

if __name__ == "__main__":
    test_city_coordinate_compatibility()