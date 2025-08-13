#!/usr/bin/env python3
"""
Translation Completeness Checker for Alt3r Bot
Verifies that all translation keys exist in both English and Russian
"""

import sys
sys.path.append('.')
from translations import TEXTS, ND_TRAITS, get_translation_coverage

def check_translation_completeness():
    """Check translation completeness between English and Russian"""
    
    print("🌐 Translation Completeness Check for Alt3r Bot")
    print("=" * 55)
    
    # Check main text translations
    print("📝 Main Text Translations:")
    print("-" * 30)
    
    en_keys = set(TEXTS['en'].keys())
    ru_keys = set(TEXTS['ru'].keys())
    
    print(f"English keys: {len(en_keys)}")
    print(f"Russian keys: {len(ru_keys)}")
    
    # Find missing translations
    missing_in_russian = en_keys - ru_keys
    missing_in_english = ru_keys - en_keys
    
    if missing_in_russian:
        print(f"\n❌ Missing in Russian ({len(missing_in_russian)} keys):")
        for key in sorted(missing_in_russian):
            print(f"  - {key}: '{TEXTS['en'][key]}'")
    
    if missing_in_english:
        print(f"\n❌ Missing in English ({len(missing_in_english)} keys):")
        for key in sorted(missing_in_english):
            print(f"  - {key}: '{TEXTS['ru'][key]}'")
    
    if not missing_in_russian and not missing_in_english:
        print("✅ All main text translations are complete!")
    
    # Check neurodivergent traits
    print(f"\n🧠 Neurodivergent Traits Translations:")
    print("-" * 30)
    
    nd_en_keys = set(ND_TRAITS['en'].keys())
    nd_ru_keys = set(ND_TRAITS['ru'].keys())
    
    print(f"English traits: {len(nd_en_keys)}")
    print(f"Russian traits: {len(nd_ru_keys)}")
    
    nd_missing_in_russian = nd_en_keys - nd_ru_keys
    nd_missing_in_english = nd_ru_keys - nd_en_keys
    
    if nd_missing_in_russian:
        print(f"\n❌ ND Traits missing in Russian ({len(nd_missing_in_russian)} traits):")
        for key in sorted(nd_missing_in_russian):
            print(f"  - {key}: '{ND_TRAITS['en'][key]}'")
    
    if nd_missing_in_english:
        print(f"\n❌ ND Traits missing in English ({len(nd_missing_in_english)} traits):")
        for key in sorted(nd_missing_in_english):
            print(f"  - {key}: '{ND_TRAITS['ru'][key]}'")
    
    if not nd_missing_in_russian and not nd_missing_in_english:
        print("✅ All neurodivergent trait translations are complete!")
    
    # Calculate overall completeness
    print(f"\n📊 Translation Coverage Summary:")
    print("-" * 30)
    
    main_text_coverage = len(en_keys.intersection(ru_keys)) / len(en_keys.union(ru_keys)) * 100
    nd_traits_coverage = len(nd_en_keys.intersection(nd_ru_keys)) / len(nd_en_keys.union(nd_ru_keys)) * 100
    
    print(f"Main Text Coverage: {main_text_coverage:.1f}%")
    print(f"ND Traits Coverage: {nd_traits_coverage:.1f}%")
    print(f"Overall Coverage: {(main_text_coverage + nd_traits_coverage) / 2:.1f}%")
    
    # Check for specific important sections
    print(f"\n🔍 Important Sections Check:")
    print("-" * 30)
    
    important_sections = {
        "Welcome & Onboarding": ["welcome", "language_prompt"],
        "Questionnaire": ["questionnaire_age", "questionnaire_gender", "questionnaire_interest", 
                         "questionnaire_city", "questionnaire_name", "questionnaire_bio", "questionnaire_photo"],
        "Main Menu": ["main_menu", "profile_menu_0", "profile_menu_1", "profile_menu_2", "profile_menu_3", 
                     "profile_menu_4", "profile_menu_5", "profile_menu_6", "profile_menu_7", "profile_menu_8"],
        "Dating": ["no_profiles", "like_sent", "skip_profile", "its_match", "new_like"],
        "Payment": ["support_title", "support_description", "payment_success", "payment_failed"],
        "Buttons": ["btn_girl", "btn_boy", "btn_girls", "btn_boys", "btn_all", "btn_yes", "btn_change", "btn_skip"]
    }
    
    for section_name, keys in important_sections.items():
        missing_count = sum(1 for key in keys if key not in ru_keys)
        if missing_count == 0:
            print(f"✅ {section_name}: Complete")
        else:
            print(f"❌ {section_name}: {missing_count}/{len(keys)} missing")
    
    # Summary and recommendations
    total_missing = len(missing_in_russian) + len(missing_in_english) + len(nd_missing_in_russian) + len(nd_missing_in_english)
    
    print(f"\n" + "=" * 55)
    print(f"🎯 Translation Status Summary")
    print(f"Total missing translations: {total_missing}")
    
    if total_missing == 0:
        print("🎉 Perfect! All translations are complete and ready for production.")
        return True
    elif total_missing <= 5:
        print("✅ Excellent! Only minor translation gaps remain.")
        return True
    elif total_missing <= 15:
        print("⚠️  Good coverage, but some important translations are missing.")
        return False
    else:
        print("❌ Significant translation gaps found. Bilingual support may be incomplete.")
        return False

if __name__ == "__main__":
    check_translation_completeness()