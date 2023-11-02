import tkinter as tk

class ParamTable:
    def __init__(self, root):
        self.root = root
        self.root.title("Parameter Table")
        
        # Example data
        self.parameters = {
            "Parameter 1": "Value 1",
            "Parameter 2": "Value 2",
            "Parameter 3": "Value 3",
            "Parameter 4": "Value 4"
        }

        self.create_ui()

    def create_ui(self):
        for index, (param, value) in enumerate(self.parameters.items()):
            # Create label for parameter name
            param_label = tk.Label(self.root, text=param, anchor="w", padx=10)
            param_label.grid(row=index, column=0, sticky="nsew")

            # Create label for parameter value
            value_label = tk.Label(self.root, text=value, anchor="w", padx=10)
            value_label.grid(row=index, column=1, sticky="nsew")

            # To change the value of a parameter dynamically:
            # value_label.config(text="New Value")
            
            self.root.grid_columnconfigure(0, weight=1)  # Adjust column weight to make it resizable
            self.root.grid_columnconfigure(1, weight=2)

if __name__ == "__main__":
    root = tk.Tk()
    table = ParamTable(root)
    root.mainloop()
