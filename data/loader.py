# data/loader.py
import pandas as pd
from data.occult_symbols_dataset import get_complete_dataset


class DataLoader:
    """Handles loading and processing data for the occult symbolism dashboard"""

    @staticmethod
    def load_data():
        """Load symbol data from the comprehensive dataset"""
        # Get the complete dataset
        raw_data = get_complete_dataset()

        # Extract the component datasets
        symbols = raw_data["symbols"]
        connections = raw_data["connections"]
        traditions = raw_data["traditions"]
        elements = raw_data["elements"]
        time_periods = raw_data["time_periods"]
        metadata = raw_data["metadata"]

        # Convert to pandas DataFrames for analysis
        symbols_df = pd.DataFrame(symbols)
        connections_df = pd.DataFrame(connections)
        traditions_df = pd.DataFrame(traditions)
        elements_df = pd.DataFrame(elements)
        time_periods_df = pd.DataFrame(time_periods)

        # Process the data for specific visualizations
        processed_data = DataLoader._process_data_for_visualizations(
            symbols_df, connections_df, traditions_df, elements_df, time_periods_df, metadata
        )

        return {
            # Original data
            "symbols_df": symbols_df,
            "connections_df": connections_df,
            "traditions_df": traditions_df,
            "elements_df": elements_df,
            "time_periods_df": time_periods_df,

            # Raw JSON data for API responses
            "raw_data": {
                "symbols": symbols,
                "connections": connections,
                "traditions": traditions,
                "elements": elements,
                "time_periods": time_periods,
                "metadata": metadata
            },

            # Processed data for specific visualizations
            "processed_data": processed_data
        }

    @staticmethod
    def _process_data_for_visualizations(symbols_df, connections_df, traditions_df,
                                         elements_df, time_periods_df, metadata):
        """Process the raw data into formats needed for specific visualizations"""
        processed = {}

        # 1. Network graph data
        processed["network_graph"] = {
            "nodes": DataLoader._prepare_network_nodes(symbols_df, metadata),
            "links": DataLoader._prepare_network_links(connections_df)
        }

        # 2. Timeline data
        processed["symbol_timeline"] = DataLoader._prepare_symbol_timeline(symbols_df)

        # 3. Tradition timeline
        processed["tradition_timeline"] = DataLoader._prepare_tradition_timeline(traditions_df)

        # 4. Element distribution
        processed["element_distribution"] = DataLoader._prepare_element_distribution(elements_df, symbols_df)

        # 5. Tradition symbol frequency
        processed["tradition_frequency"] = DataLoader._prepare_tradition_frequency(symbols_df)

        # 6. Geographic distribution
        processed["geographic_distribution"] = DataLoader._prepare_geographic_distribution(traditions_df)

        # 7. Symbol categorization
        processed["symbol_categories"] = DataLoader._prepare_symbol_categories(metadata["symbol_categories"],
                                                                               symbols_df)

        # 8. Regional influence
        processed["regional_influence"] = metadata["regional_influence"]

        # 9. Temporal transitions
        processed["tradition_transitions"] = metadata["temporal_transitions"]

        return processed

    @staticmethod
    def _prepare_network_nodes(symbols_df, metadata):
        """Prepare node data for the network visualization"""
        nodes = []

        # Get color mapping
        color_map = metadata["color_associations"]

        for _, symbol in symbols_df.iterrows():
            # Handle multi-tradition symbols
            traditions = symbol["tradition"].split("/")

            # Use the first tradition for color if multiple
            primary_tradition = traditions[0]
            color = color_map.get(primary_tradition, "#888888")  # Default gray if not found

            node = {
                "id": symbol["id"],
                "name": symbol["name"],
                "tradition": symbol["tradition"],
                "element": symbol["element"],
                "century": symbol["century_origin"],
                "color": color,
                "description": symbol["description"],
                "size": 10,  # Base size, can be adjusted based on importance
            }
            nodes.append(node)

        return nodes

    @staticmethod
    def _prepare_network_links(connections_df):
        """Prepare link data for the network visualization"""
        links = []

        for _, connection in connections_df.iterrows():
            link = {
                "source": connection["source"],
                "target": connection["target"],
                "strength": connection["strength"],
                "description": connection["description"]
            }
            links.append(link)

        return links

    @staticmethod
    def _prepare_symbol_timeline(symbols_df):
        """Prepare data for the symbol timeline visualization"""
        timeline_data = []

        # Convert century_origin to actual display years
        for _, row in symbols_df.iterrows():
            century = row["century_origin"]
            year = century * 100 - 50  # Approximate middle of century
            if century <= 0:
                year_display = f"{abs(year)} BCE"
            else:
                year_display = f"{year} CE"

            timeline_data.append({
                "id": row["id"],
                "name": row["name"],
                "tradition": row["tradition"],
                "element": row["element"],
                "year": year,
                "year_display": year_display,
                "description": row["description"]
            })

        # Sort by year
        timeline_data = sorted(timeline_data, key=lambda x: x["year"])
        return timeline_data

    @staticmethod
    def _prepare_tradition_timeline(traditions_df):
        """Prepare data for tradition timeline visualization"""
        traditions_timeline = []

        for _, tradition in traditions_df.iterrows():
            # Convert BCE/CE notation to simple year numbers
            start_year = tradition["start_century"] * 100
            end_year = tradition["end_century"] * 100

            # If end_century is 21, set it to current year
            if tradition["end_century"] == 21:
                end_year = 2025

            tradition_data = {
                "name": tradition["name"],
                "start_year": start_year,
                "end_year": end_year,
                "duration": end_year - start_year,
                "midpoint": start_year + ((end_year - start_year) / 2),
                "region": tradition["region"],
                "major_texts": tradition["major_texts"],
                "key_figures": tradition["key_figures"],
                "core_concepts": tradition["core_concepts"]
            }

            traditions_timeline.append(tradition_data)

        # Sort by start_year
        traditions_timeline = sorted(traditions_timeline, key=lambda x: x["start_year"])
        return traditions_timeline

    @staticmethod
    def _prepare_element_distribution(elements_df, symbols_df):
        """Prepare data for element distribution visualization"""
        # Count symbols by element
        element_counts = symbols_df["element"].value_counts().reset_index()
        element_counts.columns = ["element", "count"]

        # Add more detailed information from elements_df
        element_details = []

        for _, count_row in element_counts.iterrows():
            element_name = count_row["element"]
            count = count_row["count"]

            # Find matching element in elements_df
            element_detail = None
            for _, element_row in elements_df.iterrows():
                if element_row["name"] == element_name:
                    element_detail = element_row
                    break

            # If we found details, add them
            if element_detail is not None:
                element_details.append({
                    "element": element_name,
                    "count": count,
                    "description": element_detail["description"],
                    "symbols": element_detail["symbols"],
                    "traditions": element_detail["traditions"],
                    "correspondences": element_detail["correspondences"]
                })
            else:
                # Just use the count data if no details found
                element_details.append({
                    "element": element_name,
                    "count": count,
                    "description": "No detailed information available",
                    "symbols": [],
                    "traditions": [],
                    "correspondences": {}
                })

        return element_details

    @staticmethod
    def _prepare_tradition_frequency(symbols_df):
        """Prepare data for tradition frequency visualization"""
        # Group symbols by tradition and count
        tradition_counts = symbols_df["tradition"].value_counts().reset_index()
        tradition_counts.columns = ["tradition", "count"]

        # Split multi-tradition entries (like "Egyptian/Greek")
        expanded_counts = []
        for _, row in tradition_counts.iterrows():
            if "/" in row["tradition"]:
                traditions = row["tradition"].split("/")
                for t in traditions:
                    expanded_counts.append({"tradition": t, "count": row["count"]})
            else:
                expanded_counts.append({"tradition": row["tradition"], "count": row["count"]})

        # Combine counts for the same tradition
        result = {}
        for item in expanded_counts:
            trad = item["tradition"]
            if trad in result:
                result[trad] += item["count"]
            else:
                result[trad] = item["count"]

        return [{"tradition": k, "count": v} for k, v in result.items()]

    @staticmethod
    def _prepare_geographic_distribution(traditions_df):
        """Prepare data for geographic visualization"""
        # Count by region
        regions = {}
        for _, tradition in traditions_df.iterrows():
            region = tradition["region"]
            if region in regions:
                regions[region] += 1
            else:
                regions[region] = 1

        # Handle multi-region entries
        expanded_regions = {}
        for region, count in regions.items():
            if "/" in region:
                sub_regions = region.split("/")
                for r in sub_regions:
                    if r in expanded_regions:
                        expanded_regions[r] += count
                    else:
                        expanded_regions[r] = count
            else:
                if region in expanded_regions:
                    expanded_regions[region] += count
                else:
                    expanded_regions[region] = count

        return [{"region": k, "count": v} for k, v in expanded_regions.items()]

    @staticmethod
    def _prepare_symbol_categories(categories, symbols_df):
        """Prepare symbol category data for visualization"""
        result = []

        for category in categories:
            # Get the symbols in this category
            category_symbols = []
            for symbol_id in category["symbols"]:
                symbol = symbols_df[symbols_df["id"] == symbol_id]
                if not symbol.empty:
                    category_symbols.append({
                        "id": symbol_id,
                        "name": symbol["name"].values[0],
                        "tradition": symbol["tradition"].values[0],
                        "element": symbol["element"].values[0]
                    })

            result.append({
                "name": category["name"],
                "symbols": category_symbols,
                "count": len(category_symbols)
            })

        return result