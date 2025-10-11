"""Visualization recommendation engine"""
from typing import List, Dict, Any, Optional
from enum import Enum
import re


class ChartType(str, Enum):
    """Supported chart types"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    TABLE = "table"


class ColumnType(str, Enum):
    """Column data types for visualization"""
    TEMPORAL = "temporal"
    QUANTITATIVE = "quantitative"
    NOMINAL = "nominal"
    ORDINAL = "ordinal"


class VizRecommender:
    """Recommend visualizations based on query results"""
    
    # Temporal patterns
    TEMPORAL_PATTERNS = [
        r"date", r"time", r"timestamp", r"year", r"month", r"day",
        r"created", r"updated", r"_at$", r"_date$"
    ]
    
    # Numeric types
    NUMERIC_TYPES = {
        "integer", "int", "bigint", "smallint",
        "decimal", "numeric", "real", "double",
        "float", "money"
    }
    
    def __init__(self):
        pass
    
    def recommend_charts(
        self,
        columns: List[str],
        rows: List[List[Any]],
        column_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend chart types based on data shape and content.
        
        Returns list of chart specifications with Vega-Lite JSON.
        """
        if not columns or not rows:
            return []
        
        # Infer column types if not provided
        if not column_types:
            column_types = self._infer_column_types(columns, rows)
        
        recommendations = []
        col_info = list(zip(columns, column_types))
        
        # Analyze data structure
        temporal_cols = [col for col, ctype in col_info if ctype == ColumnType.TEMPORAL]
        numeric_cols = [col for col, ctype in col_info if ctype == ColumnType.QUANTITATIVE]
        categorical_cols = [col for col, ctype in col_info if ctype in (ColumnType.NOMINAL, ColumnType.ORDINAL)]
        
        # Recommendation logic
        if temporal_cols and numeric_cols:
            # Time series: line chart
            recommendations.append(
                self._create_line_chart(columns, temporal_cols[0], numeric_cols[0])
            )
            # Also area chart
            recommendations.append(
                self._create_area_chart(columns, temporal_cols[0], numeric_cols[0])
            )
        
        if categorical_cols and numeric_cols:
            # Category + number: bar chart
            recommendations.append(
                self._create_bar_chart(columns, categorical_cols[0], numeric_cols[0])
            )
            
            # If few categories, also pie chart
            if len(rows) <= 10:
                recommendations.append(
                    self._create_pie_chart(columns, categorical_cols[0], numeric_cols[0])
                )
        
        if len(numeric_cols) >= 2:
            # Two numeric: scatter plot
            recommendations.append(
                self._create_scatter_chart(columns, numeric_cols[0], numeric_cols[1])
            )
        
        # Always include table as fallback
        recommendations.append({
            "title": "Data Table",
            "type": ChartType.TABLE,
            "description": "Tabular view of all data"
        })
        
        return recommendations[:3]  # Return top 3
    
    def _infer_column_types(
        self,
        columns: List[str],
        rows: List[List[Any]]
    ) -> List[str]:
        """Infer column types from names and sample data"""
        types = []
        
        for i, col_name in enumerate(columns):
            col_lower = col_name.lower()
            
            # Check for temporal patterns in name
            if any(re.search(pattern, col_lower) for pattern in self.TEMPORAL_PATTERNS):
                types.append(ColumnType.TEMPORAL)
                continue
            
            # Check sample values
            sample_values = [row[i] for row in rows[:10] if row[i] is not None]
            
            if not sample_values:
                types.append(ColumnType.NOMINAL)
                continue
            
            # Check if numeric
            if all(isinstance(v, (int, float)) for v in sample_values):
                types.append(ColumnType.QUANTITATIVE)
            else:
                types.append(ColumnType.NOMINAL)
        
        return types
    
    def _create_line_chart(
        self,
        columns: List[str],
        x_col: str,
        y_col: str
    ) -> Dict[str, Any]:
        """Create line chart specification"""
        return {
            "title": f"{y_col} over {x_col}",
            "type": ChartType.LINE,
            "description": f"Line chart showing trend of {y_col} over time",
            "vega_lite": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {"name": "table"},
                "mark": {"type": "line", "point": True, "tooltip": True},
                "encoding": {
                    "x": {
                        "field": x_col,
                        "type": "temporal",
                        "title": x_col
                    },
                    "y": {
                        "field": y_col,
                        "type": "quantitative",
                        "title": y_col
                    }
                },
                "width": 600,
                "height": 400
            }
        }
    
    def _create_area_chart(
        self,
        columns: List[str],
        x_col: str,
        y_col: str
    ) -> Dict[str, Any]:
        """Create area chart specification"""
        return {
            "title": f"{y_col} over {x_col} (Area)",
            "type": ChartType.AREA,
            "description": f"Area chart showing {y_col} trend",
            "vega_lite": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {"name": "table"},
                "mark": {"type": "area", "opacity": 0.7, "tooltip": True},
                "encoding": {
                    "x": {
                        "field": x_col,
                        "type": "temporal",
                        "title": x_col
                    },
                    "y": {
                        "field": y_col,
                        "type": "quantitative",
                        "title": y_col
                    }
                },
                "width": 600,
                "height": 400
            }
        }
    
    def _create_bar_chart(
        self,
        columns: List[str],
        x_col: str,
        y_col: str
    ) -> Dict[str, Any]:
        """Create bar chart specification"""
        return {
            "title": f"{y_col} by {x_col}",
            "type": ChartType.BAR,
            "description": f"Bar chart comparing {y_col} across {x_col}",
            "vega_lite": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {"name": "table"},
                "mark": {"type": "bar", "tooltip": True},
                "encoding": {
                    "x": {
                        "field": x_col,
                        "type": "nominal",
                        "title": x_col
                    },
                    "y": {
                        "field": y_col,
                        "type": "quantitative",
                        "title": y_col
                    }
                },
                "width": 600,
                "height": 400
            }
        }
    
    def _create_pie_chart(
        self,
        columns: List[str],
        category_col: str,
        value_col: str
    ) -> Dict[str, Any]:
        """Create pie chart specification"""
        return {
            "title": f"{value_col} distribution by {category_col}",
            "type": ChartType.PIE,
            "description": f"Pie chart showing proportion of {value_col}",
            "vega_lite": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {"name": "table"},
                "mark": {"type": "arc", "tooltip": True},
                "encoding": {
                    "theta": {
                        "field": value_col,
                        "type": "quantitative"
                    },
                    "color": {
                        "field": category_col,
                        "type": "nominal"
                    }
                },
                "view": {"stroke": None},
                "width": 400,
                "height": 400
            }
        }
    
    def _create_scatter_chart(
        self,
        columns: List[str],
        x_col: str,
        y_col: str
    ) -> Dict[str, Any]:
        """Create scatter plot specification"""
        return {
            "title": f"{y_col} vs {x_col}",
            "type": ChartType.SCATTER,
            "description": f"Scatter plot showing relationship between {x_col} and {y_col}",
            "vega_lite": {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "data": {"name": "table"},
                "mark": {"type": "point", "tooltip": True},
                "encoding": {
                    "x": {
                        "field": x_col,
                        "type": "quantitative",
                        "title": x_col
                    },
                    "y": {
                        "field": y_col,
                        "type": "quantitative",
                        "title": y_col
                    }
                },
                "width": 600,
                "height": 400
            }
        }

