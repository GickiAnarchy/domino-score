# Domino Hand Movement Fix

## Problem
The domino tiles in your hand don't move/reorganize properly when tiles are played. This happens because:

1. **Conflicting behaviors**: The tiles use `Scatter` (which makes them draggable) but are placed in a `MDGridLayout` (which has fixed positioning)
2. **GridLayout limitations**: When you remove a tile, the GridLayout tries to reorganize but the Scatter behavior interferes
3. **Scatter translation**: Even with `do_translation` disabled in some places, the position management is inconsistent

## Solution Options

### OPTION 1: Disable Dragging in Hand (Simplest Fix)
Just disable the Scatter movement for tiles while they're in your hand. They only need to be draggable once on the board.

**File: screens/board.py**
In the `_refresh_hand()` method, add these lines after creating each tile:

```python
def _refresh_hand(self):
    hand = self.ids.hand_area
    hand.clear_widgets()
    tw, th = self.tile_size()

    for model in self.hand_tiles:
        tile = DominoTileWidget(
            value_top=model.value_top,
            value_bottom=model.value_bottom,
            size=(tw, th)
        )
        tile.model = model
        
        # ADD THESE LINES - Disable scatter behavior in hand
        tile.do_translation_x = False
        tile.do_translation_y = False
        tile.do_scale = False
        
        hand.add_widget(tile)
```

### OPTION 2: Use FloatLayout Instead of GridLayout (Better Control)
Replace the GridLayout with a FloatLayout and manually position tiles. This gives you full control.

**Step 1: Update domino.kv**
Replace the `<BoardScreen>:` section with:

```yaml
<BoardScreen>:
    name: "board"

    MDBoxLayout:
        orientation: "vertical"

        RelativeLayout:
            id: board_area

        FloatLayout:
            id: hand_area
            size_hint_y: None
            height: dp(180)
            
            canvas.before:
                Color:
                    rgba: 0.1, 0.1, 0.1, 0.3
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(10)]
```

**Step 2: Update screens/board.py**
Replace the entire `_refresh_hand()` method:

```python
def _refresh_hand(self):
    """Refresh hand with proper positioning in FloatLayout"""
    hand = self.ids.hand_area
    hand.clear_widgets()
    tw, th = self.tile_size()
    
    # Calculate total width needed for all tiles
    total_tiles = len(self.hand_tiles)
    spacing = dp(6)
    total_width = (total_tiles * tw) + ((total_tiles - 1) * spacing)
    
    # Center the tiles horizontally
    start_x = (hand.width - total_width) / 2 if hand.width > total_width else dp(8)
    y_pos = dp(8)  # Fixed y position at bottom of hand area

    for i, model in enumerate(self.hand_tiles):
        tile = DominoTileWidget(
            value_top=model.value_top,
            value_bottom=model.value_bottom,
            size=(tw, th)
        )
        tile.model = model
        
        # Disable dragging for tiles in hand
        tile.do_translation_x = False
        tile.do_translation_y = False
        tile.do_scale = False
        tile.do_rotation = False
        
        # Set position explicitly
        x_pos = start_x + (i * (tw + spacing))
        tile.pos = (x_pos, y_pos)
        
        hand.add_widget(tile)
```

Also update `play_tile()` to add a small delay for smoother refresh:

```python
def play_tile(self, model):
    """Move tile from hand to board"""
    if model in self.hand_tiles:
        self.hand_tiles.remove(model)
        self.board_tiles.append(model)
        # Small delay for smoother transition
        Clock.schedule_once(self.refresh_ui, 0.05)
```

And update `on_enter()` to give the UI time to size:

```python
def on_enter(self, *args):
    self.hand_tiles = []
    self.board_tiles = []
    self._setup_new_game()
    # Give screen time to size before calculating positions
    Clock.schedule_once(self.refresh_ui, 0.1)
```

## Recommendation

**Start with Option 1** - it's the quickest fix with minimal changes. Just add those 3 lines to disable dragging in the hand.

If you still have issues or want more control over positioning, then implement **Option 2** with the FloatLayout.

## Testing

After applying the fix:
1. Go to the Board screen
2. Tap tiles in your hand to play them to the board
3. The remaining tiles should stay in place properly
4. As you play tiles, the hand should show the correct remaining tiles

## Additional Enhancement (Optional)

For even smoother animations when tiles are removed, you could add a fade-out animation:

```python
from kivy.animation import Animation

def play_tile(self, model):
    if model in self.hand_tiles:
        # Find the tile widget
        for tile in self.ids.hand_area.children:
            if tile.model == model:
                # Fade out animation
                anim = Animation(opacity=0, duration=0.2)
                anim.bind(on_complete=lambda *x: self._complete_play(model))
                anim.start(tile)
                return
    
def _complete_play(self, model):
    self.hand_tiles.remove(model)
    self.board_tiles.append(model)
    Clock.schedule_once(self.refresh_ui, 0.05)
```

Let me know which option you'd like to try first!
