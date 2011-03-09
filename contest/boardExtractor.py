def vectorize(layout, cellLayout):
  return [layout.width, layout.height, len(layout.walls.asList(True)), len(layout.food.asList(True)), len(layout.capsules), len(cellLayout.cells)]
