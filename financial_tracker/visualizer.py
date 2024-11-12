import logging
from typing import Optional
from dataclasses import dataclass, field

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

from financial_tracker.data_processor import DataProcessor


@dataclass
class FinancialVisualizer:
    """
    A class to represent a financial data visualizer using Dash framework.

    Attributes:
        processor (DataProcessor): Instance of DataProcessor for data handling.
        app (dash.Dash): Dash application instance for visualization.
    """

    processor: DataProcessor
    app: dash.Dash = field(init=False, default_factory=lambda: dash.Dash(__name__))

    def __post_init__(self):
        """
        Initializes the Dash app and sets up the layout.

        Logs a warning if no data is available for visualization.
        """
        if self.processor.data.empty:
            logging.warning("No data available for visualization.")
        else:
            logging.info("Data loaded successfully for visualization.")
        self.setup_layout()

    def setup_layout(self) -> None:
        """
        Sets up the layout of the Dash app with dropdowns and graphs.
        """
        self.app.layout = html.Div(
            className="container",
            children=[
                html.H1("Financial Dashboard", className="header"),
                html.Div(
                    className="flex-around",
                    children=[
                        self.create_dropdown_container(
                            "category_dropdown",
                            options=[
                                {"label": cat, "value": cat}
                                for cat in self.processor.data["category"].unique()
                            ],
                            placeholder="Select a category",
                        ),
                        self.create_dropdown_container(
                            "period_dropdown",
                            options=[
                                {"label": period, "value": period}
                                for period in self.processor.data["period"].unique()
                            ],
                            placeholder="Select a period",
                        ),
                    ],
                ),
                html.Div(
                    className="flex-container",
                    children=[
                        self.create_graph_container("category_pie_chart"),
                        self.create_graph_container("monthly_bar_chart"),
                    ],
                ),
                html.Div(
                    className="flex-container",
                    children=[
                        self.create_graph_container("comparison_chart"),
                    ],
                ),
            ],
        )
        self.setup_callbacks()

    def create_graph_container(self, graph_id: str) -> html.Div:
        """
        Creates a container for a graph.

        Args:
            graph_id (str): The ID of the graph.

        Returns:
            html.Div: A Div element containing a graph component.
        """
        return html.Div([dcc.Graph(id=graph_id)], className="graph-container")

    def create_dropdown_container(
        self, dropdown_id: str, options: list, placeholder: str
    ) -> html.Div:
        """
        Creates a container for a dropdown menu.

        Args:
            dropdown_id (str): The ID of the dropdown.
            options (list): List of options for the dropdown menu.
            placeholder (str): Placeholder text for the dropdown.

        Returns:
            html.Div: A Div element containing a dropdown component.
        """
        return html.Div(
            [
                dcc.Dropdown(
                    id=dropdown_id,
                    options=options,
                    placeholder=placeholder,
                    className="dropdown-dark",
                ),
            ],
            className="dropdown-container",
        )

    def setup_callbacks(self) -> None:
        """
        Defines the callback functions for interactive elements of the Dash app.
        """

        @self.app.callback(
            Output("category_pie_chart", "figure"),
            Input("category_dropdown", "value"),
        )
        def update_pie_chart(selected_category: Optional[str]) -> go.Figure:
            """
            Updates the pie chart based on the selected category.

            Args:
                selected_category (Optional[str]): The selected category from the dropdown.

            Returns:
                go.Figure: A Plotly Figure object for the pie chart.
            """
            try:
                if selected_category:
                    data = self.processor.get_subcategory_summary(selected_category)
                    fig = px.pie(
                        data,
                        names="subcategory",
                        values="sum rub",
                        title=f"Expenses for {selected_category}",
                        template="plotly_dark",
                    )
                else:
                    data = self.processor.get_category_summary()
                    fig = px.pie(
                        data,
                        names="category",
                        values="sum rub",
                        title="Expenses by Category",
                        template="plotly_dark",
                    )

                # Update pie chart text and layout
                fig.update_traces(textinfo="percent+label")
                fig.update_layout(
                    margin=dict(t=30, b=30, l=30, r=180),
                    height=500,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.1,
                        font=dict(size=12),
                        itemsizing="constant",
                        title_text="Categories",
                    ),
                    showlegend=True,
                    uniformtext_minsize=10,
                    uniformtext_mode="hide",
                )
                fig.update_traces(
                    hole=0.1,
                    marker=dict(line=dict(color="#000000", width=0.5)),
                )
                return fig
            except Exception as e:
                logging.error(f"Failed to update pie chart: {e}")
                return go.Figure()

        @self.app.callback(
            Output("monthly_bar_chart", "figure"),
            Input("period_dropdown", "value"),
        )
        def update_bar_chart(selected_period: Optional[str]) -> go.Figure:
            """
            Updates the bar chart based on the selected period.

            Args:
                selected_period (Optional[str]): The selected period from the dropdown.

            Returns:
                go.Figure: A Plotly Figure object for the bar chart.
            """
            try:
                if selected_period:
                    data = self.processor.filter_by_period(selected_period)
                    data = data.groupby("category")["sum rub"].sum().reset_index()
                    fig = px.bar(
                        data,
                        x="category",
                        y="sum rub",
                        title=f"Expenses for {selected_period}",
                        template="plotly_dark",
                    )
                else:
                    data = self.processor.get_monthly_summary()
                    fig = px.bar(
                        data,
                        x="month",
                        y="sum rub",
                        title="Monthly Expenses",
                        template="plotly_dark",
                    )
                fig.update_layout(
                    plot_bgcolor="#1f1f1f", paper_bgcolor="#1f1f1f", font_color="white"
                )
                return fig
            except Exception as e:
                logging.error(f"Failed to update bar chart: {e}")
                return go.Figure()

        @self.app.callback(
            Output("category_dropdown", "value"),
            Input("category_pie_chart", "clickData"),
        )
        def update_category_on_click(clickData: dict) -> Optional[str]:
            """
            Updates the category dropdown based on click data from the pie chart.

            Args:
                clickData (dict): Click data from the pie chart.

            Returns:
                Optional[str]: The selected category, or None if no selection.
            """
            try:
                if clickData:
                    selected_category = clickData["points"][0]["label"]
                    logging.info(
                        f"Selected category from pie chart: {selected_category}"
                    )
                    return selected_category
                return None
            except Exception as e:
                logging.error(f"Failed to update category from pie chart click: {e}")
                return None

        @self.app.callback(
            Output("period_dropdown", "value"),
            Input("monthly_bar_chart", "clickData"),
        )
        def update_period_on_click(clickData):
            """
            Update the period dropdown based on click on the bar chart.

            When a bar (period) is clicked, format the date as "YYYY-MM"
            and update the period dropdown with the selected value.
            """
            try:
                if clickData:
                    selected_period = clickData["points"][0]["x"]
                    formatted_period = selected_period[:7]  # Оставляем только "YYYY-MM"
                    logging.info(f"Selected period from bar chart: {formatted_period}")
                    return formatted_period
                return None
            except Exception as e:
                logging.error(f"Failed to update period from bar chart click: {e}")
                return None

        @self.app.callback(
            Output("comparison_chart", "figure"), Input("category_dropdown", "value")
        )
        def update_comparison_chart(selected_category: Optional[str]) -> go.Figure:
            """
            Updates the comparison chart showing mean and median expenses by category.

            Args:
                selected_category (Optional[str]): The selected category from the dropdown.

            Returns:
                go.Figure: A Plotly Figure object for the comparison chart.
            """
            try:
                data = self.processor.get_category_mean_median()
                fig = go.Figure()

                # Добавляем столбцы для среднего и медианного значений
                fig.add_trace(
                    go.Bar(
                        x=data["category"],
                        y=data["mean_expense"],
                        name="Mean Expense",
                        marker_color="indianred",
                    )
                )
                fig.add_trace(
                    go.Bar(
                        x=data["category"],
                        y=data["median_expense"],
                        name="Median Expense",
                        marker_color="lightsalmon",
                    )
                )

                fig.update_layout(
                    barmode="group",
                    title="Comparison of Mean and Median Expenses by Category",
                    xaxis_title="Category",
                    yaxis_title="Expense (RUB)",
                    template="plotly_dark",
                    legend=dict(x=0.9, y=1, traceorder="normal", font=dict(size=12)),
                )
                return fig
            except Exception as e:
                logging.error(f"Failed to update comparison chart: {e}")
                return go.Figure()

    def run(self) -> None:
        """
        Runs the Dash application server.
        """
        self.app.run_server(debug=True)
