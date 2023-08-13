from kivy.lang import Builder

Builder.load_file('draw_shape/drawing.kv')

"""
* on page open :
    initial drawing : mesh_drawing
        a + button stands for new :
            on_press the mesh_vertices should be saved in private file and the second drawing should start with new points.            
"""
