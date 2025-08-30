# Code Review and Fix Plan

## Issues Identified

### 1. Missing `on_test_connection` method in TranslationFrame
**File**: `modules/ui_components.py`  
**Issue**: The `TranslationFrame` class has a "Test Connection" button that calls `self.on_test_connection`, but this method is missing.  
**Location**: Line 246 in `create_widgets()` method  
**Fix**: Add the missing `on_test_connection` method to the `TranslationFrame` class.

### 2. Missing `on_test_connection` callback setup in GUI
**File**: `gui.py`  
**Issue**: The `TranslationFrame` callbacks are not set up with the connection test callback.  
**Location**: Line 95-97 in `setup_callbacks()` method  
**Fix**: Add the missing `test_connection_callback` parameter to the `set_callbacks` call.

### 3. Missing `test_connection` method in GUI class
**File**: `gui.py`  
**Issue**: The GUI class references `self.test_connection` but this method doesn't exist.  
**Location**: Line 95-97 in `setup_callbacks()` method  
**Fix**: Add the missing `test_connection` method to the `VideoSubtitleGUI` class.

### 4. Missing `on_test_connection` method in TranslationFrame
**File**: `modules/ui_components.py`  
**Issue**: The `TranslationFrame` class is missing the `on_test_connection` method that should handle the button click.  
**Location**: After line 320 in the class  
**Fix**: Add the missing method to handle the connection test button click.

### 5. Inconsistent callback handling
**File**: `modules/ui_components.py`  
**Issue**: The `TranslationFrame.set_callbacks()` method accepts `test_connection_callback` but it's not being used consistently.  
**Location**: Line 320-325 in `set_callbacks()` method  
**Fix**: Ensure the callback is properly stored and used.

### 6. Missing import for `on_test_connection` method
**File**: `modules/ui_components.py`  
**Issue**: The `on_test_connection` method is referenced but not defined.  
**Location**: Line 246 in `create_widgets()` method  
**Fix**: Add the missing method definition.

## Fix Plan

### Step 1: Fix TranslationFrame class
- Add missing `on_test_connection` method to `TranslationFrame` class
- Ensure proper callback handling

### Step 2: Fix GUI callback setup
- Add missing `test_connection` method to `VideoSubtitleGUI` class
- Update callback setup to include connection test callback

### Step 3: Test the fixes
- Verify that the GUI launches without errors
- Test that the "Test Connection" button works properly

### Step 4: Verify all callbacks work
- Test translation functionality
- Test connection testing functionality
- Ensure no missing method errors

## Implementation Order

1. Fix `modules/ui_components.py` - add missing method
2. Fix `gui.py` - add missing method and callback setup
3. Test the application
4. Document any additional issues found

## Expected Outcome

After implementing these fixes:
- The GUI should launch without AttributeError
- The "Test Connection" button should be functional
- All callback methods should be properly defined
- The application should be stable and functional
