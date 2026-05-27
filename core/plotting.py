import plotly.graph_objects as go
import numpy as np
from typing import Callable, Tuple, List, Optional, Any

def plot_1d_functions(
    funcs: List[Tuple[Callable, str, str]],
    x_bounds: Tuple[float, float],
    resolution: int = 500,
    title: str = "Wykres funkcji"
) -> go.Figure:
    x_vals = np.linspace(x_bounds[0], x_bounds[1], resolution)
    fig = go.Figure()
    
    for func, name, color in funcs:
        y_vals = func(x_vals)
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=name, line=dict(color=color)))
        
    fig.update_layout(title=title, template="plotly_white")
    return fig

def plot_heatmap_2d(
    func: Callable,
    x_bounds: Tuple[float, float],
    y_bounds: Tuple[float, float],
    resolution: int = 100,
    title: str = "Mapa ciepła"
) -> go.Figure:
    x_vals = np.linspace(x_bounds[0], x_bounds[1], resolution)
    y_vals = np.linspace(y_bounds[0], y_bounds[1], resolution)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = func(X.flatten(), Y.flatten()).reshape(X.shape)
    
    fig = go.Figure(data=go.Contour(z=Z, x=x_vals, y=y_vals, colorscale="Viridis"))
    fig.update_layout(title=title, template="plotly_white")
    return fig

def plot_point_cloud(
    points: List[Tuple[float, float]],
    title: str = "Chmura punktów",
    color: str = "blue"
) -> go.Figure:
    x_vals = [p[0] for p in points]
    y_vals = [p[1] for p in points]
    
    fig = go.Figure(data=go.Scatter(x=x_vals, y=y_vals, mode='markers', marker=dict(color=color, size=5)))
    fig.update_layout(title=title, template="plotly_white")
    return fig
