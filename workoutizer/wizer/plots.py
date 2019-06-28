import numpy as np

from bokeh.plotting import figure, show, output_file

# from workoutizer.wizer.models import Activity
# print(f"activity from plots: {Activity.objects.get(1)}")


def plot_activities():
    x = np.linspace(0, 2 * np.pi, 2000)
    y = np.sin(x)
    output_file('test.html')
    plot = figure(plot_height=300, plot_width=600, y_range=(-5, 5))
    plot.line(x, y, color="#2222aa", line_width=3)
    return plot
