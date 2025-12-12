"""
Verification script for Lore Generation Agents
Tests the variety injector, state manager, and agent imports.
"""
import logging
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()


def test_imports():
    """Test that all lore modules can be imported."""
    print("=== Testing Imports ===")
    
    try:
        from backend.services.variety_injector import VarietyInjector
        print("✓ VarietyInjector imported")
    except Exception as e:
        print(f"✗ VarietyInjector import failed: {e}")
        return False
    
    try:
        from backend.agents.lore_state_manager import LoreStateManager
        print("✓ LoreStateManager imported")
    except Exception as e:
        print(f"✗ LoreStateManager import failed: {e}")
        return False
    
    try:
        from backend.agents.era_architect import EraArchitectAgent
        print("✓ EraArchitectAgent imported")
    except Exception as e:
        print(f"✗ EraArchitectAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.faction_forge import FactionForgeAgent
        print("✓ FactionForgeAgent imported")
    except Exception as e:
        print(f"✗ FactionForgeAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.soul_weaver import SoulWeaverAgent
        print("✓ SoulWeaverAgent imported")
    except Exception as e:
        print(f"✗ SoulWeaverAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.conflict_designer import ConflictDesignerAgent
        print("✓ ConflictDesignerAgent imported")
    except Exception as e:
        print(f"✗ ConflictDesignerAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.pathweaver import PathweaverAgent
        print("✓ PathweaverAgent imported")
    except Exception as e:
        print(f"✗ PathweaverAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.lore_orchestrator import LoreOrchestratorAgent
        print("✓ LoreOrchestratorAgent imported")
    except Exception as e:
        print(f"✗ LoreOrchestratorAgent import failed: {e}")
        return False
    
    print("All imports successful!")
    return True


def test_variety_injector():
    """Test the variety injector service."""
    print("\n=== Testing Variety Injector ===")
    
    from backend.services.variety_injector import VarietyInjector
    
    injector = VarietyInjector()
    
    # Check name pools loaded
    print(f"Name pools loaded: {list(injector.name_pools.keys())}")
    assert len(injector.name_pools) >= 1, "Should have at least 1 name pool"
    
    # Check event templates
    print(f"Event templates loaded: {len(injector.event_templates)}")
    assert len(injector.event_templates) >= 1, "Should have at least 1 event template"
    
    # Check banned words
    print(f"Banned words loaded: {len(injector.banned_words)}")
    assert len(injector.banned_words) >= 1, "Should have banned words"
    
    # Check game inspirations
    print(f"Game inspirations loaded: {list(injector.game_inspirations.keys())}")
    assert len(injector.game_inspirations) >= 1, "Should have game inspirations"
    
    # Test seed generation
    seeds = injector.get_generation_seeds()
    print(f"\nGenerated seeds:")
    print(f"  Cultures: {seeds['name_cultures']}")
    print(f"  Emotion: {seeds['emotion_seed']}")
    print(f"  Aesthetic: {seeds['aesthetic_seed']}")
    print(f"  Conflict: {seeds['conflict_seed']}")
    print(f"  Game reference: {seeds['game_reference']}")
    print(f"  Event inspirations: {[e.get('name') for e in seeds['event_inspirations']]}")
    
    assert seeds['name_cultures'], "Should have name cultures"
    assert seeds['emotion_seed'], "Should have emotion seed"
    assert seeds['aesthetic_seed'], "Should have aesthetic seed"
    
    print("✓ VarietyInjector tests passed!")
    return True


def test_state_manager():
    """Test the lore state manager."""
    print("\n=== Testing Lore State Manager ===")
    
    from backend.agents.lore_state_manager import LoreStateManager
    
    state_mgr = LoreStateManager()
    
    # Test project info
    state_mgr.set_project_info("Test Chronicles", "dark_fantasy")
    state = state_mgr.get_state()
    assert state['project_name'] == "Test Chronicles"
    print("✓ Project info setting works")
    
    # Test era management
    test_era = {
        "name": "Age of Testing",
        "duration": "100 years",
        "summary": "A time of unit tests",
        "is_cataclysm": False
    }
    state_mgr.add_era(test_era)
    assert len(state_mgr.get_state()['eras']) == 1
    print("✓ Era management works")
    
    # Test faction management
    test_faction = {
        "name": "The Debuggers",
        "type": "guild",
        "ideology": "All bugs must be fixed"
    }
    state_mgr.add_faction(test_faction)
    assert len(state_mgr.get_state()['factions']) == 1
    print("✓ Faction management works")
    
    # Test character management
    test_char = {
        "name": "Tester McTestface",
        "archetype": "The Shadow",
        "motivation": "To find all edge cases"
    }
    state_mgr.add_character(test_char)
    assert len(state_mgr.get_state()['characters']) == 1
    print("✓ Character management works")
    
    # Test route management
    state_mgr.set_route("light", {
        "name": "Path of Coverage",
        "chapters": [],
        "ending": "100% test coverage achieved"
    })
    assert state_mgr.get_state()['routes']['light']['name'] == "Path of Coverage"
    print("✓ Route management works")
    
    # Test phase tracking
    state_mgr.complete_phase("eras")
    assert state_mgr.is_phase_completed("eras")
    assert not state_mgr.is_phase_completed("factions")
    print("✓ Phase tracking works")
    
    print("✓ LoreStateManager tests passed!")
    return True


def verify_lore_generation(minimal=True):
    """Run a minimal lore generation test (uses API calls)."""
    print("\n=== Testing Lore Generation ===")
    
    if minimal:
        print("Running minimal generation test (1 era, 2 factions, 2 characters, 1 conflict)...")
        print("This will make API calls to Gemini.")
        
    from backend.agents.lore_orchestrator import LoreOrchestratorAgent
    
    orchestrator = LoreOrchestratorAgent()
    
    if minimal:
        # Stop after eras for a quick test
        result = orchestrator.start_generation(
            project_name="Test Game Lore",
            num_eras=2,
            num_factions=2,
            num_characters=2,
            num_conflicts=1,
            num_chapters_per_route=2,
            stop_after="eras"  # Stop early for quick test
        )
        
        print(f"\nResult status: {result.get('status')}")
        print(f"Phase: {result.get('phase')}")
        
        if result.get('state'):
            state = result['state']
            print(f"Project name: {state.get('project_name')}")
            print(f"Eras generated: {len(state.get('eras', []))}")
            print(f"Variety seeds used: {state.get('variety_seeds', {}).get('name_cultures', [])}")
            
            if state.get('eras'):
                print("\nFirst era:")
                era = state['eras'][0]
                print(f"  Name: {era.get('name')}")
                print(f"  Summary: {era.get('summary', '')[:100]}...")
        
        return result.get('status') in ['PAUSED', 'COMPLETE']
    
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 50)
    print("LORE GENERATION VERIFICATION")
    print("=" * 50)
    
    # Run tests
    all_passed = True
    
    all_passed = test_imports() and all_passed
    all_passed = test_variety_injector() and all_passed
    all_passed = test_state_manager() and all_passed
    
    print("\n" + "=" * 50)
    
    # Ask about API test
    if all_passed:
        print("\nBasic tests passed! Do you want to run a minimal lore generation test?")
        print("This will make API calls to Gemini and may take a minute.")
        print("Enter 'y' to run, anything else to skip:")
        
        try:
            response = input().strip().lower()
            if response == 'y':
                success = verify_lore_generation(minimal=True)
                if success:
                    print("\n✓ Lore generation test passed!")
                else:
                    print("\n✗ Lore generation test had issues")
                    all_passed = False
        except EOFError:
            print("Skipping API test (no input available)")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED")
    print("=" * 50)
