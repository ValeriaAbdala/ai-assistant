import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
import base64
import io
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class VisualizationService:
    def __init__(self):
        # Set style for matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Plotly default config
        self.plotly_config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
        }

    def create_ticket_dashboard(self, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive ticket dashboard"""
        try:
            if not tickets:
                return {"error": "No tickets data provided"}
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(tickets)
            
            # Generate multiple visualizations
            charts = {
                "severity_distribution": self._create_severity_chart(df),
                "revenue_impact_chart": self._create_revenue_impact_chart(df),
                "team_workload_chart": self._create_team_workload_chart(df),
                "status_timeline": self._create_status_timeline(df),
                "priority_matrix": self._create_priority_matrix(df)
            }
            
            # Generate summary metrics
            metrics = self._calculate_dashboard_metrics(df)
            
            return {
                "charts": charts,
                "metrics": metrics,
                "total_tickets": len(tickets),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating ticket dashboard: {str(e)}")
            return {"error": str(e)}

    def _create_severity_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create severity distribution pie chart"""
        try:
            severity_counts = df['severity'].value_counts()
            
            # Create Plotly pie chart
            fig = go.Figure(data=[go.Pie(
                labels=severity_counts.index,
                values=severity_counts.values,
                hole=0.3,
                marker_colors=['#FF6B6B', '#FFA726', '#66BB6A', '#42A5F5']
            )])
            
            fig.update_layout(
                title="Ticket Distribution by Severity",
                font=dict(size=14),
                showlegend=True,
                height=400
            )
            
            return {
                "type": "pie",
                "plotly_json": fig.to_json(),
                "data_summary": severity_counts.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating severity chart: {str(e)}")
            return {"error": str(e)}

    def _create_revenue_impact_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create revenue impact bar chart"""
        try:
            # Filter tickets with revenue impact
            impact_df = df[df['revenue_impact'] > 0].copy()
            
            if impact_df.empty:
                return {"error": "No revenue impact data available"}
            
            # Sort by revenue impact
            impact_df = impact_df.sort_values('revenue_impact', ascending=True)
            
            # Create horizontal bar chart
            fig = go.Figure(data=[go.Bar(
                x=impact_df['revenue_impact'],
                y=impact_df['id'],
                orientation='h',
                marker_color='#FF6B6B',
                text=impact_df['revenue_impact'].apply(lambda x: f'${x:,.0f}'),
                textposition='auto'
            )])
            
            fig.update_layout(
                title="Revenue Impact by Ticket",
                xaxis_title="Revenue Impact ($)",
                yaxis_title="Ticket ID",
                height=max(400, len(impact_df) * 30),
                font=dict(size=12)
            )
            
            return {
                "type": "bar",
                "plotly_json": fig.to_json(),
                "total_impact": impact_df['revenue_impact'].sum()
            }
            
        except Exception as e:
            logger.error(f"Error creating revenue impact chart: {str(e)}")
            return {"error": str(e)}

    def _create_team_workload_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create team workload distribution chart"""
        try:
            # Group by assignee
            assignee_counts = df['assignee'].value_counts()
            
            # Create bar chart
            fig = go.Figure(data=[go.Bar(
                x=assignee_counts.index,
                y=assignee_counts.values,
                marker_color='#66BB6A',
                text=assignee_counts.values,
                textposition='auto'
            )])
            
            fig.update_layout(
                title="Ticket Distribution by Team Member",
                xaxis_title="Team Member",
                yaxis_title="Number of Tickets",
                height=400,
                xaxis_tickangle=-45
            )
            
            return {
                "type": "bar",
                "plotly_json": fig.to_json(),
                "workload_balance": self._calculate_workload_balance(assignee_counts)
            }
            
        except Exception as e:
            logger.error(f"Error creating team workload chart: {str(e)}")
            return {"error": str(e)}

    def _create_status_timeline(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create status distribution chart"""
        try:
            status_counts = df['status'].value_counts()
            
            # Create donut chart
            fig = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.4,
                marker_colors=['#42A5F5', '#FFA726', '#66BB6A', '#FF6B6B']
            )])
            
            fig.update_layout(
                title="Ticket Status Distribution",
                font=dict(size=14),
                height=400,
                annotations=[dict(text='Status', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            
            return {
                "type": "donut",
                "plotly_json": fig.to_json(),
                "status_summary": status_counts.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating status timeline: {str(e)}")
            return {"error": str(e)}

    def _create_priority_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create priority vs impact matrix"""
        try:
            # Create scatter plot of impact vs customers affected
            fig = go.Figure()
            
            severities = df['severity'].unique()
            colors = {'critical': '#FF6B6B', 'high': '#FFA726', 'medium': '#66BB6A', 'low': '#42A5F5'}
            
            for severity in severities:
                severity_df = df[df['severity'] == severity]
                
                fig.add_trace(go.Scatter(
                    x=severity_df['affected_customers'],
                    y=severity_df['revenue_impact'],
                    mode='markers+text',
                    name=severity.title(),
                    text=severity_df['id'],
                    textposition='top center',
                    marker=dict(
                        size=10,
                        color=colors.get(severity, '#42A5F5'),
                        opacity=0.7
                    )
                ))
            
            fig.update_layout(
                title="Priority Matrix: Revenue Impact vs Customers Affected",
                xaxis_title="Customers Affected",
                yaxis_title="Revenue Impact ($)",
                height=500,
                showlegend=True
            )
            
            return {
                "type": "scatter",
                "plotly_json": fig.to_json(),
                "matrix_insights": self._analyze_priority_matrix(df)
            }
            
        except Exception as e:
            logger.error(f"Error creating priority matrix: {str(e)}")
            return {"error": str(e)}

    def create_analytics_charts(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create charts for analytics results"""
        try:
            charts = {}
            
            # Correlation analysis chart
            if 'correlation_insights' in analytics_data:
                charts['correlation_chart'] = self._create_correlation_chart(analytics_data)
            
            # Prediction timeline
            if 'predictions' in analytics_data:
                charts['prediction_chart'] = self._create_prediction_timeline(analytics_data['predictions'])
            
            # Team optimization chart
            if 'workload_analysis' in analytics_data:
                charts['team_optimization_chart'] = self._create_team_optimization_chart(analytics_data['workload_analysis'])
            
            return {
                "analytics_charts": charts,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating analytics charts: {str(e)}")
            return {"error": str(e)}

    def _create_correlation_chart(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create correlation analysis visualization"""
        try:
            metrics = analytics_data.get('metrics', {})
            
            # Create metrics overview chart
            categories = ['Total Tickets', 'Critical Tickets', 'High Impact', 'Revenue Impact ($)']
            values = [
                metrics.get('total_tickets', 0),
                metrics.get('critical_tickets', 0),
                metrics.get('high_impact_tickets', 0),
                metrics.get('total_revenue_impact', 0) / 1000  # Convert to thousands
            ]
            
            fig = go.Figure(data=[go.Bar(
                x=categories,
                y=values,
                marker_color=['#42A5F5', '#FF6B6B', '#FFA726', '#66BB6A'],
                text=[f'{v:,.0f}' for v in values],
                textposition='auto'
            )])
            
            fig.update_layout(
                title="Correlation Analysis Metrics",
                height=400,
                xaxis_tickangle=-45
            )
            
            return {
                "type": "bar",
                "plotly_json": fig.to_json()
            }
            
        except Exception as e:
            logger.error(f"Error creating correlation chart: {str(e)}")
            return {"error": str(e)}

    def _create_prediction_timeline(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create prediction timeline visualization"""
        try:
            if not predictions:
                return {"error": "No prediction data available"}
            
            # Sort by predicted loss
            predictions_sorted = sorted(predictions, key=lambda x: x.get('predicted_additional_loss', 0), reverse=True)
            
            ticket_ids = [p['ticket_id'] for p in predictions_sorted[:10]]  # Top 10
            current_impact = [p['current_impact'] for p in predictions_sorted[:10]]
            predicted_loss = [p['predicted_additional_loss'] for p in predictions_sorted[:10]]
            
            fig = go.Figure()
            
            # Current impact
            fig.add_trace(go.Bar(
                name='Current Impact',
                x=ticket_ids,
                y=current_impact,
                marker_color='#42A5F5'
            ))
            
            # Predicted additional loss
            fig.add_trace(go.Bar(
                name='Predicted Additional Loss',
                x=ticket_ids,
                y=predicted_loss,
                marker_color='#FF6B6B'
            ))
            
            fig.update_layout(
                title="Impact Prediction: Current vs Predicted Loss",
                xaxis_title="Ticket ID",
                yaxis_title="Financial Impact ($)",
                barmode='group',
                height=500,
                xaxis_tickangle=-45
            )
            
            return {
                "type": "grouped_bar",
                "plotly_json": fig.to_json()
            }
            
        except Exception as e:
            logger.error(f"Error creating prediction timeline: {str(e)}")
            return {"error": str(e)}

    def _create_team_optimization_chart(self, workload_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create team optimization visualization"""
        try:
            if not workload_analysis:
                return {"error": "No workload data available"}
            
            members = list(workload_analysis.keys())
            ticket_counts = [data['ticket_count'] for data in workload_analysis.values()]
            critical_counts = [data['critical_tickets'] for data in workload_analysis.values()]
            workload_scores = [data['workload_score'] for data in workload_analysis.values()]
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=1, cols=1,
                secondary_y=True,
                subplot_titles=["Team Workload Analysis"]
            )
            
            # Bar chart for ticket counts
            fig.add_trace(
                go.Bar(name="Total Tickets", x=members, y=ticket_counts, marker_color='#42A5F5'),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Bar(name="Critical Tickets", x=members, y=critical_counts, marker_color='#FF6B6B'),
                secondary_y=False
            )
            
            # Line chart for workload score
            fig.add_trace(
                go.Scatter(name="Workload Score", x=members, y=workload_scores, 
                          mode='lines+markers', marker_color='#66BB6A', line=dict(width=3)),
                secondary_y=True
            )
            
            # Update layout
            fig.update_xaxes(title_text="Team Member", tickangle=-45)
            fig.update_yaxes(title_text="Number of Tickets", secondary_y=False)
            fig.update_yaxes(title_text="Workload Score", secondary_y=True)
            
            fig.update_layout(
                title="Team Workload Distribution",
                height=500,
                showlegend=True
            )
            
            return {
                "type": "mixed",
                "plotly_json": fig.to_json()
            }
            
        except Exception as e:
            logger.error(f"Error creating team optimization chart: {str(e)}")
            return {"error": str(e)}

    def _calculate_dashboard_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary metrics for dashboard"""
        return {
            "total_tickets": len(df),
            "critical_tickets": len(df[df['severity'] == 'critical']),
            "total_revenue_impact": df['revenue_impact'].sum(),
            "avg_customers_affected": df['affected_customers'].mean(),
            "open_tickets": len(df[df['status'].isin(['open', 'in-progress'])]),
            "completion_rate": len(df[df['status'] == 'resolved']) / len(df) * 100
        }

    def _calculate_workload_balance(self, assignee_counts) -> Dict[str, Any]:
        """Calculate workload balance metrics"""
        if len(assignee_counts) == 0:
            return {"balance_score": 0, "recommendation": "No assignee data"}
        
        std_dev = assignee_counts.std()
        mean_workload = assignee_counts.mean()
        balance_score = max(0, 100 - (std_dev / mean_workload * 100)) if mean_workload > 0 else 0
        
        return {
            "balance_score": round(balance_score, 1),
            "std_deviation": round(std_dev, 2),
            "recommendation": "Well balanced" if balance_score > 80 else "Consider rebalancing workload"
        }

    def _analyze_priority_matrix(self, df: pd.DataFrame) -> List[str]:
        """Analyze priority matrix and provide insights"""
        insights = []
        
        # High impact, high customers affected
        high_impact_high_customers = df[
            (df['revenue_impact'] > df['revenue_impact'].median()) & 
            (df['affected_customers'] > df['affected_customers'].median())
        ]
        
        if not high_impact_high_customers.empty:
            insights.append(f"{len(high_impact_high_customers)} tickets have both high revenue impact and many affected customers")
        
        # Critical tickets with low impact
        critical_low_impact = df[(df['severity'] == 'critical') & (df['revenue_impact'] < 1000)]
        if not critical_low_impact.empty:
            insights.append(f"{len(critical_low_impact)} critical tickets have unexpectedly low revenue impact")
        
        return insights

    def export_chart_as_image(self, chart_data: Dict[str, Any], format: str = "png") -> str:
        """Export chart as base64 encoded image"""
        try:
            if chart_data.get("type") == "error":
                return None
            
            # For Plotly charts, convert to image
            if "plotly_json" in chart_data:
                fig = go.Figure(json.loads(chart_data["plotly_json"]))
                img_bytes = fig.to_image(format=format, width=800, height=600)
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/{format};base64,{img_base64}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error exporting chart as image: {str(e)}")
            return None