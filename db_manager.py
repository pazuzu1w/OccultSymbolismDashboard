# db_manager.py
# CLI tool for manually managing the occult symbols database

import argparse
import json
import os
import sys
import logging
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from app import create_app
from models.database import db, Symbol, Tradition, Connection, Element, TimePeriod

# Set up rich console for better display
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("db_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("db_manager")


# Initialize Flask app and database connection
def init_db():
    """Initialize the database connection"""
    app = create_app()
    app.app_context().push()  # Make the app context active for the current thread
    return app


def list_symbols(args):
    """List symbols in the database with optional filtering"""
    query = Symbol.query

    # Apply filters if provided
    if args.tradition:
        query = query.filter(Symbol.tradition.like(f"%{args.tradition}%"))
    if args.element:
        # This requires retrieving elements from the relationship
        elements = Element.query.filter(Element.name.like(f"%{args.element}%")).all()
        element_ids = [e.id for e in elements]
        if element_ids:
            # This assumes you have a many-to-many relationship
            query = query.filter(Symbol.elements.any(Element.id.in_(element_ids)))
    if args.period:
        # Handle BCE with negative numbers
        try:
            if "BCE" in args.period.upper():
                century = -int(args.period.upper().replace("BCE", "").strip())
            else:
                century = int(args.period.replace("CE", "").strip())
            query = query.filter(Symbol.century_origin == century)
        except ValueError:
            console.print(f"[red]Invalid period format: {args.period}. Use format like '5 CE' or '3 BCE'[/red]")

    # Execute query
    symbols = query.all()

    if not symbols:
        console.print("[yellow]No symbols found matching the criteria.[/yellow]")
        return

    # Create and display table
    table = Table(title=f"Symbols in Database ({len(symbols)} found)")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Tradition", style="blue")
    table.add_column("Element", style="magenta")
    table.add_column("Century", justify="right")
    table.add_column("Description", no_wrap=False)

    for symbol in symbols:
        # Format century as BCE/CE
        century = symbol.century_origin
        if century < 0:
            century_display = f"{abs(century)} BCE"
        else:
            century_display = f"{century} CE"

        # Get element names
        element_names = ", ".join([e.name for e in symbol.elements]) if hasattr(symbol, 'elements') else ""

        # Truncate description if too long
        description = symbol.description[:100] + "..." if symbol.description and len(symbol.description) > 100 else (
                    symbol.description or "")

        table.add_row(
            str(symbol.id),
            symbol.name,
            symbol.tradition,
            element_names,
            century_display,
            description
        )

    console.print(table)


def list_traditions(args):
    """List traditions in the database"""
    traditions = Tradition.query.all()

    if not traditions:
        console.print("[yellow]No traditions found in the database.[/yellow]")
        return

    table = Table(title=f"Traditions in Database ({len(traditions)} found)")
    table.add_column("Name", style="green")
    table.add_column("Time Period", style="cyan")
    table.add_column("Region", style="blue")
    table.add_column("Major Texts", no_wrap=False)

    for tradition in traditions:
        # Format time period
        if tradition.start_century < 0:
            start = f"{abs(tradition.start_century)} BCE"
        else:
            start = f"{tradition.start_century} CE"

        if tradition.end_century < 0:
            end = f"{abs(tradition.end_century)} BCE"
        elif tradition.end_century == 21:
            end = "Present"
        else:
            end = f"{tradition.end_century} CE"

        time_period = f"{start} to {end}"

        # Format major texts
        major_texts = json.loads(tradition.major_texts) if tradition.major_texts else []
        texts_display = ", ".join(major_texts[:3])
        if len(major_texts) > 3:
            texts_display += f" (+{len(major_texts) - 3} more)"

        table.add_row(
            tradition.name,
            time_period,
            tradition.region,
            texts_display
        )

    console.print(table)


def list_connections(args):
    """List connections between symbols"""
    connections = Connection.query.all()

    if not connections:
        console.print("[yellow]No connections found in the database.[/yellow]")
        return

    table = Table(title=f"Symbol Connections ({len(connections)} found)")
    table.add_column("Source", style="green")
    table.add_column("Target", style="green")
    table.add_column("Strength", style="cyan", justify="right")
    table.add_column("Description", no_wrap=False)

    for connection in connections:
        # Get symbol names
        source = Symbol.query.get(connection.source_id)
        target = Symbol.query.get(connection.target_id)

        if not source or not target:
            continue

        table.add_row(
            f"{source.name} (ID: {source.id})",
            f"{target.name} (ID: {target.id})",
            f"{connection.strength:.2f}",
            connection.description[:100] + "..." if connection.description and len(connection.description) > 100 else (
                        connection.description or "")
        )

    console.print(table)


def add_symbol(args):
    """Add a new symbol to the database"""
    console.print(Panel.fit("[bold]Add New Symbol[/bold]", border_style="green"))

    # Get required information
    name = Prompt.ask("[bold]Symbol Name[/bold]")
    tradition = Prompt.ask("[bold]Tradition[/bold]", default="Unknown")

    # Get elements
    element_input = Prompt.ask("[bold]Element(s)[/bold] (comma-separated)", default="Unknown")
    elements = [e.strip() for e in element_input.split(',')]

    # Get century of origin
    while True:
        century_input = Prompt.ask("[bold]Century Origin[/bold] (e.g., '5 CE' or '3 BCE')", default="Unknown")
        if century_input.lower() == "unknown":
            century_origin = 0
            break

        try:
            if "BCE" in century_input.upper():
                century_origin = -int(century_input.upper().replace("BCE", "").strip())
            else:
                century_origin = int(century_input.replace("CE", "").strip())
            break
        except ValueError:
            console.print("[red]Invalid format. Please use format like '5 CE' or '3 BCE'[/red]")

    description = Prompt.ask("[bold]Description[/bold]", default="")
    usage = Prompt.ask("[bold]Usage[/bold]", default="")
    visual_elements_input = Prompt.ask("[bold]Visual Elements[/bold] (comma-separated)", default="")
    visual_elements = [v.strip() for v in visual_elements_input.split(',') if v.strip()]

    # Create new symbol
    try:
        new_symbol = Symbol(
            name=name,
            tradition=tradition,
            century_origin=century_origin,
            description=description,
            usage=usage,
            visual_elements=json.dumps(visual_elements)
        )

        # Add elements
        for element_name in elements:
            if element_name.lower() != "unknown":
                # Find or create element
                element = Element.query.filter(Element.name == element_name).first()
                if not element:
                    element = Element(name=element_name)
                    db.session.add(element)
                    db.session.flush()  # Get ID without committing

                new_symbol.elements.append(element)

        db.session.add(new_symbol)
        db.session.commit()

        console.print(f"[green]Symbol '{name}' added successfully with ID {new_symbol.id}[/green]")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error adding symbol: {str(e)}[/red]")


def add_tradition(args):
    """Add a new tradition to the database"""
    console.print(Panel.fit("[bold]Add New Tradition[/bold]", border_style="green"))

    # Get required information
    name = Prompt.ask("[bold]Tradition Name[/bold]")

    # Check if tradition already exists
    existing = Tradition.query.filter(Tradition.name == name).first()
    if existing:
        console.print(f"[yellow]Tradition '{name}' already exists. Use edit command to modify it.[/yellow]")
        return

    region = Prompt.ask("[bold]Region[/bold]", default="Unknown")

    # Get start century
    while True:
        start_century_input = Prompt.ask("[bold]Start Century[/bold] (e.g., '5 CE' or '3 BCE')", default="Unknown")
        if start_century_input.lower() == "unknown":
            start_century = 0
            break

        try:
            if "BCE" in start_century_input.upper():
                start_century = -int(start_century_input.upper().replace("BCE", "").strip())
            else:
                start_century = int(start_century_input.replace("CE", "").strip())
            break
        except ValueError:
            console.print("[red]Invalid format. Please use format like '5 CE' or '3 BCE'[/red]")

    # Get end century
    while True:
        end_century_input = Prompt.ask("[bold]End Century[/bold] (e.g., '5 CE' or 'Present')", default="Present")
        if end_century_input.lower() == "present":
            end_century = 21
            break

        try:
            if "BCE" in end_century_input.upper():
                end_century = -int(end_century_input.upper().replace("BCE", "").strip())
            else:
                end_century = int(end_century_input.replace("CE", "").strip())
            break
        except ValueError:
            console.print("[red]Invalid format. Please use format like '5 CE' or 'Present'[/red]")

    major_texts_input = Prompt.ask("[bold]Major Texts[/bold] (comma-separated)", default="")
    major_texts = [t.strip() for t in major_texts_input.split(',') if t.strip()]

    key_figures_input = Prompt.ask("[bold]Key Figures[/bold] (comma-separated)", default="")
    key_figures = [f.strip() for f in key_figures_input.split(',') if f.strip()]

    core_concepts_input = Prompt.ask("[bold]Core Concepts[/bold] (comma-separated)", default="")
    core_concepts = [c.strip() for c in core_concepts_input.split(',') if c.strip()]

    # Create new tradition
    try:
        new_tradition = Tradition(
            name=name,
            region=region,
            start_century=start_century,
            end_century=end_century,
            major_texts=json.dumps(major_texts),
            key_figures=json.dumps(key_figures),
            core_concepts=json.dumps(core_concepts)
        )

        db.session.add(new_tradition)
        db.session.commit()

        console.print(f"[green]Tradition '{name}' added successfully[/green]")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error adding tradition: {str(e)}[/red]")


def add_connection(args):
    """Add a connection between two symbols"""
    console.print(Panel.fit("[bold]Add Symbol Connection[/bold]", border_style="green"))

    # List available symbols
    symbols = Symbol.query.all()
    if len(symbols) < 2:
        console.print("[yellow]Need at least 2 symbols to create a connection.[/yellow]")
        return

    table = Table(title="Available Symbols")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="green")

    for symbol in symbols:
        table.add_row(str(symbol.id), symbol.name)

    console.print(table)

    # Get source and target symbols
    while True:
        source_id = Prompt.ask("[bold]Source Symbol ID[/bold]")
        try:
            source_id = int(source_id)
            source = Symbol.query.get(source_id)
            if source:
                break
            console.print(f"[red]Symbol with ID {source_id} not found[/red]")
        except ValueError:
            console.print("[red]Please enter a valid ID number[/red]")

    while True:
        target_id = Prompt.ask("[bold]Target Symbol ID[/bold]")
        try:
            target_id = int(target_id)
            if target_id == source_id:
                console.print("[red]Target must be different from source[/red]")
                continue

            target = Symbol.query.get(target_id)
            if target:
                break
            console.print(f"[red]Symbol with ID {target_id} not found[/red]")
        except ValueError:
            console.print("[red]Please enter a valid ID number[/red]")

    # Check if connection already exists
    existing = Connection.query.filter_by(source_id=source_id, target_id=target_id).first()
    if existing:
        console.print(f"[yellow]Connection from '{source.name}' to '{target.name}' already exists.[/yellow]")
        if not Confirm.ask("Do you want to update it?"):
            return

        # Update existing connection
        while True:
            strength_input = Prompt.ask("[bold]Connection Strength[/bold] (0.0-1.0)", default=str(existing.strength))
            try:
                strength = float(strength_input)
                if 0 <= strength <= 1:
                    break
                console.print("[red]Strength must be between 0.0 and 1.0[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")

        description = Prompt.ask("[bold]Connection Description[/bold]", default=existing.description or "")

        try:
            existing.strength = strength
            existing.description = description
            db.session.commit()
            console.print(f"[green]Connection updated successfully[/green]")
        except Exception as e:
            db.session.rollback()
            console.print(f"[red]Error updating connection: {str(e)}[/red]")
        return

    # Create new connection
    while True:
        strength_input = Prompt.ask("[bold]Connection Strength[/bold] (0.0-1.0)", default="0.5")
        try:
            strength = float(strength_input)
            if 0 <= strength <= 1:
                break
            console.print("[red]Strength must be between 0.0 and 1.0[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

    description = Prompt.ask("[bold]Connection Description[/bold]", default="")

    try:
        new_connection = Connection(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            description=description
        )

        db.session.add(new_connection)
        db.session.commit()

        console.print(f"[green]Connection from '{source.name}' to '{target.name}' added successfully[/green]")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error adding connection: {str(e)}[/red]")


def edit_symbol(args):
    """Edit an existing symbol"""
    # First, find the symbol to edit
    if args.id:
        symbol_id = args.id
    else:
        symbol_id = Prompt.ask("[bold]Enter symbol ID to edit[/bold]")

    try:
        symbol_id = int(symbol_id)
    except ValueError:
        console.print("[red]Invalid ID. Please enter a numeric ID.[/red]")
        return

    symbol = Symbol.query.get(symbol_id)
    if not symbol:
        console.print(f"[red]Symbol with ID {symbol_id} not found[/red]")
        return

    console.print(Panel.fit(f"[bold]Editing Symbol: {symbol.name} (ID: {symbol.id})[/bold]", border_style="yellow"))

    # Display current values
    console.print("[cyan]Current Values:[/cyan]")
    console.print(f"Name: {symbol.name}")
    console.print(f"Tradition: {symbol.tradition}")
    console.print(f"Elements: {', '.join([e.name for e in symbol.elements]) if hasattr(symbol, 'elements') else ''}")

    century = symbol.century_origin
    if century < 0:
        century_display = f"{abs(century)} BCE"
    else:
        century_display = f"{century} CE"
    console.print(f"Century Origin: {century_display}")

    console.print(f"Description: {symbol.description}")
    console.print(f"Usage: {symbol.usage}")

    visual_elements = json.loads(symbol.visual_elements) if symbol.visual_elements else []
    console.print(f"Visual Elements: {', '.join(visual_elements)}")

    # Get updated values
    name = Prompt.ask("[bold]Name[/bold]", default=symbol.name)
    tradition = Prompt.ask("[bold]Tradition[/bold]", default=symbol.tradition)

    # Handle elements
    current_elements = ", ".join([e.name for e in symbol.elements]) if hasattr(symbol, 'elements') else ""
    element_input = Prompt.ask("[bold]Element(s)[/bold] (comma-separated)", default=current_elements)
    elements = [e.strip() for e in element_input.split(',') if e.strip()]

    # Get century of origin
    while True:
        century_input = Prompt.ask("[bold]Century Origin[/bold] (e.g., '5 CE' or '3 BCE')", default=century_display)
        if century_input.lower() == "unknown":
            century_origin = 0
            break

        try:
            if "BCE" in century_input.upper():
                century_origin = -int(century_input.upper().replace("BCE", "").strip())
            else:
                century_origin = int(century_input.replace("CE", "").strip())
            break
        except ValueError:
            console.print("[red]Invalid format. Please use format like '5 CE' or '3 BCE'[/red]")

    description = Prompt.ask("[bold]Description[/bold]", default=symbol.description or "")
    usage = Prompt.ask("[bold]Usage[/bold]", default=symbol.usage or "")

    visual_elements_str = ", ".join(visual_elements)
    visual_elements_input = Prompt.ask("[bold]Visual Elements[/bold] (comma-separated)", default=visual_elements_str)
    new_visual_elements = [v.strip() for v in visual_elements_input.split(',') if v.strip()]

    # Update the symbol
    try:
        symbol.name = name
        symbol.tradition = tradition
        symbol.century_origin = century_origin
        symbol.description = description
        symbol.usage = usage
        symbol.visual_elements = json.dumps(new_visual_elements)

        # Update elements if we have that relationship
        if hasattr(symbol, 'elements'):
            # Clear existing elements
            symbol.elements = []

            # Add new elements
            for element_name in elements:
                # Find or create element
                element = Element.query.filter(Element.name == element_name).first()
                if not element:
                    element = Element(name=element_name)
                    db.session.add(element)
                    db.session.flush()  # Get ID without committing

                symbol.elements.append(element)

        db.session.commit()
        console.print(f"[green]Symbol '{name}' updated successfully[/green]")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error updating symbol: {str(e)}[/red]")


def edit_tradition(args):
    """Edit an existing tradition"""
    # Get tradition to edit
    if args.name:
        tradition_name = args.name
    else:
        tradition_name = Prompt.ask("[bold]Enter tradition name to edit[/bold]")

    tradition = Tradition.query.filter(Tradition.name == tradition_name).first()
    if not tradition:
        console.print(f"[red]Tradition '{tradition_name}' not found[/red]")
        return

    console.print(Panel.fit(f"[bold]Editing Tradition: {tradition.name}[/bold]", border_style="yellow"))

    # Display current values
    console.print("[cyan]Current Values:[/cyan]")
    console.print(f"Name: {tradition.name}")
    console.print(f"Region: {tradition.region}")

    # Format time period display
    if tradition.start_century < 0:
        start_display = f"{abs(tradition.start_century)} BCE"
    else:
        start_display = f"{tradition.start_century} CE"

    if tradition.end_century < 0:
        end_display = f"{abs(tradition.end_century)} BCE"
    elif tradition.end_century == 21:
        end_display = "Present"
    else:
        end_display = f"{tradition.end_century} CE"

    console.print(f"Time Period: {start_display} to {end_display}")

    major_texts = json.loads(tradition.major_texts) if tradition.major_texts else []
    console.print(f"Major Texts: {', '.join(major_texts)}")

    key_figures = json.loads(tradition.key_figures) if tradition.key_figures else []
    console.print(f"Key Figures: {', '.join(key_figures)}")

    core_concepts = json.loads(tradition.core_concepts) if tradition.core_concepts else []
    console.print(f"Core Concepts: {', '.join(core_concepts)}")

    # Get updated values
    name = Prompt.ask("[bold]Name[/bold]", default=tradition.name)
    region = Prompt.ask("[bold]Region[/bold]", default=tradition.region)

    # Get start century
    while True:
        start_century_input = Prompt.ask("[bold]Start Century[/bold] (e.g., '5 CE' or '3 BCE')", default=start_display)
        try:
            if "BCE" in start_century_input.upper():
                start_century = -int(start_century_input.upper().replace("BCE", "").strip())
            else:
                start_century = int(start_century_input.replace("CE", "").strip())
            break
        except ValueError:
            console.print("[red]Invalid format. Please use format like '5 CE' or '3 BCE'[/red]")

    # Get end century
    while True:
        end_century_input = Prompt.ask("[bold]End Century[/bold] (e.g., '5 CE' or 'Present')", default=end_display)
        if end_century_input.lower() == "present":
            end_century = 21
            break

        try:
            if "BCE" in end_century_input.upper():
                end_century = -int(end_century_input.upper().replace("BCE", "").strip())
            else:
                end_century = int(end_century_input.replace("CE", "").strip())
            break
        except ValueError:
            console.print("[red]Invalid format. Please use format like '5 CE' or 'Present'[/red]")

    major_texts_input = Prompt.ask("[bold]Major Texts[/bold] (comma-separated)", default=", ".join(major_texts))
    new_major_texts = [t.strip() for t in major_texts_input.split(',') if t.strip()]

    key_figures_input = Prompt.ask("[bold]Key Figures[/bold] (comma-separated)", default=", ".join(key_figures))
    new_key_figures = [f.strip() for f in key_figures_input.split(',') if f.strip()]

    core_concepts_input = Prompt.ask("[bold]Core Concepts[/bold] (comma-separated)", default=", ".join(core_concepts))
    new_core_concepts = [c.strip() for c in core_concepts_input.split(',') if c.strip()]

    # Update tradition
    try:
        # If name is changing, check it doesn't conflict
        if name != tradition.name:
            existing = Tradition.query.filter(Tradition.name == name).first()
            if existing:
                console.print(f"[red]Another tradition with name '{name}' already exists[/red]")
                return

        tradition.name = name
        tradition.region = region
        tradition.start_century = start_century
        tradition.end_century = end_century
        tradition.major_texts = json.dumps(new_major_texts)
        tradition.key_figures = json.dumps(new_key_figures)
        tradition.core_concepts = json.dumps(new_core_concepts)

        db.session.commit()
        console.print(f"[green]Tradition '{name}' updated successfully[/green]")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error updating tradition: {str(e)}[/red]")


def delete_symbol(args):
    """Delete a symbol from the database"""
    # Find the symbol to delete
    if args.id:
        symbol_id = args.id
    else:
        symbol_id = Prompt.ask("[bold]Enter symbol ID to delete[/bold]")

    try:
        symbol_id = int(symbol_id)
    except ValueError:
        console.print("[red]Invalid ID. Please enter a numeric ID.[/red]")
        return

    symbol = Symbol.query.get(symbol_id)
    if not symbol:
        console.print(f"[red]Symbol with ID {symbol_id} not found[/red]")
        return

    console.print(f"[yellow]About to delete symbol: {symbol.name} (ID: {symbol.id})[/yellow]")

    # Check for connections that use this symbol
    source_connections = Connection.query.filter_by(source_id=symbol_id).all()
    target_connections = Connection.query.filter_by(target_id=symbol_id).all()

    if source_connections or target_connections:
        console.print(
            f"[yellow]This symbol has {len(source_connections) + len(target_connections)} connections that will also be deleted.[/yellow]")

    if not Confirm.ask("Are you sure you want to delete this symbol and its connections?"):
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return

    try:
        # Delete connections first
        for conn in source_connections:
            db.session.delete(conn)
        for conn in target_connections:
            db.session.delete(conn)

        # Then delete the symbol
        db.session.delete(symbol)
        db.session.commit()

        console.print(f"[green]Symbol '{symbol.name}' and its connections deleted successfully[/green]")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error deleting symbol: {str(e)}[/red]")


def delete_tradition(args):
    """Delete a tradition from the database"""
    # Get tradition to delete
    if args.name:
        tradition_name = args.name
    else:
        tradition_name = Prompt.ask("[bold]Enter tradition name to delete[/bold]")

    tradition = Tradition.query.filter(Tradition.name == tradition_name).first()
    if not tradition:
        console.print(f"[red]Tradition '{tradition_name}' not found[/red]")
        return

    console.print(f"[yellow]About to delete tradition: {tradition.name}[/yellow]")

    # Check for symbols that use this tradition
    affected_symbols = Symbol.query.filter(Symbol.tradition == tradition.name).all()
    if affected_symbols:
        console.print(f"[yellow]There are {len(affected_symbols)} symbols associated with this tradition.[/yellow]")
        console.print(
            "[yellow]Deleting this tradition will NOT delete these symbols, but they will have an orphaned tradition reference.[/yellow]")

    if not Confirm.ask("Are you sure you want to delete this tradition?"):
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return

    try:
        db.session.delete(tradition)
        db.session.commit()

        console.print(f"[green]Tradition '{tradition.name}' deleted successfully[/green]")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error deleting tradition: {str(e)}[/red]")


def delete_connection(args):
    """Delete a connection between symbols"""
    console.print(Panel.fit("[bold]Delete Symbol Connection[/bold]", border_style="red"))

    # List connections
    connections = Connection.query.all()
    if not connections:
        console.print("[yellow]No connections found in the database.[/yellow]")
        return

    table = Table(title="Symbol Connections")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Source", style="green")
    table.add_column("Target", style="green")
    table.add_column("Strength", justify="right")

    for i, connection in enumerate(connections, 1):
        source = Symbol.query.get(connection.source_id)
        target = Symbol.query.get(connection.target_id)

        if not source or not target:
            continue

        table.add_row(
            str(i),
            f"{source.name} (ID: {source.id})",
            f"{target.name} (ID: {target.id})",
            f"{connection.strength:.2f}"
        )

    console.print(table)

    # Get connection to delete
    while True:
        connection_index = Prompt.ask("[bold]Enter connection index to delete[/bold] (or 'cancel')")
        if connection_index.lower() == 'cancel':
            console.print("[yellow]Deletion cancelled.[/yellow]")
            return

        try:
            index = int(connection_index)
            if 1 <= index <= len(connections):
                connection = connections[index - 1]
                break
            console.print(f"[red]Please enter a number between 1 and {len(connections)}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

    # Confirm deletion
    source = Symbol.query.get(connection.source_id)
    target = Symbol.query.get(connection.target_id)

    console.print(f"[yellow]About to delete connection from '{source.name}' to '{target.name}'[/yellow]")

    if not Confirm.ask("Are you sure?"):
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return

    try:
        db.session.delete(connection)
        db.session.commit()

        console.print(f"[green]Connection deleted successfully[/green]")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error deleting connection: {str(e)}[/red]")


def export_data(args):
    """Export database to JSON file"""
    output_file = args.file or "occult_symbols_export.json"

    console.print(f"[cyan]Exporting database to {output_file}...[/cyan]")

    try:
        # Get all data from database
        symbols = Symbol.query.all()
        traditions = Tradition.query.all()
        connections = Connection.query.all()
        elements = Element.query.all()
        time_periods = TimePeriod.query.all() if hasattr(TimePeriod, 'query') else []

        # Convert to dictionaries
        symbols_data = [symbol.to_dict() for symbol in symbols]
        traditions_data = [tradition.to_dict() for tradition in traditions]
        connections_data = [connection.to_dict() for connection in connections]
        elements_data = [element.to_dict() for element in elements] if hasattr(Element, 'to_dict') else []
        time_periods_data = [period.to_dict() for period in time_periods] if hasattr(TimePeriod, 'to_dict') else []

        # Create export data
        export_data = {
            "symbols": symbols_data,
            "traditions": traditions_data,
            "connections": connections_data,
            "elements": elements_data,
            "time_periods": time_periods_data,
            "export_info": {
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "symbol_count": len(symbols_data),
                "tradition_count": len(traditions_data),
                "connection_count": len(connections_data)
            }
        }

        # Create directory if needed
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        console.print(f"[green]Data exported successfully to {output_file}[/green]")
        console.print(
            f"Exported {len(symbols_data)} symbols, {len(traditions_data)} traditions, and {len(connections_data)} connections")
    except Exception as e:
        console.print(f"[red]Error exporting data: {str(e)}[/red]")


def import_data(args):
    """Import data from JSON file"""
    input_file = args.file
    if not input_file or not os.path.exists(input_file):
        console.print(f"[red]File {input_file} not found[/red]")
        return

    console.print(f"[cyan]Importing data from {input_file}...[/cyan]")

    try:
        # Load data from file
        with open(input_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)

        # Validate data structure
        required_keys = ['symbols', 'traditions', 'connections']
        for key in required_keys:
            if key not in import_data:
                console.print(f"[red]Error: File is missing required '{key}' data[/red]")
                return

        # Check if we should merge or replace
        mode = args.mode or Prompt.ask(
            "[bold]Import mode[/bold]",
            choices=["merge", "replace"],
            default="merge"
        )

        if mode == "replace" and not Confirm.ask(
                "[yellow]Replace mode will delete all existing data. Are you sure?[/yellow]"
        ):
            console.print("[yellow]Import cancelled.[/yellow]")
            return

        # Process import based on mode
        if mode == "replace":
            # Delete all existing data
            Connection.query.delete()
            Symbol.query.delete()
            Tradition.query.delete()
            Element.query.delete() if hasattr(Element, 'query') else None
            TimePeriod.query.delete() if hasattr(TimePeriod, 'query') else None
            db.session.commit()

            console.print("[green]Existing data deleted successfully[/green]")

        # Import symbols
        symbol_count = 0
        for symbol_data in import_data['symbols']:
            # Skip if symbol exists in merge mode
            if mode == "merge" and Symbol.query.get(symbol_data.get('id')):
                continue

            try:
                # Create new symbol
                new_symbol = Symbol(
                    id=symbol_data.get('id'),
                    name=symbol_data.get('name', ''),
                    tradition=symbol_data.get('tradition', ''),
                    century_origin=symbol_data.get('century_origin', 0),
                    description=symbol_data.get('description', ''),
                    usage=symbol_data.get('usage', ''),
                    visual_elements=json.dumps(symbol_data.get('visual_elements', []))
                )
                db.session.add(new_symbol)
                symbol_count += 1
            except Exception as e:
                console.print(f"[red]Error importing symbol {symbol_data.get('id')}: {str(e)}[/red]")

        # Import traditions
        tradition_count = 0
        for tradition_data in import_data['traditions']:
            # Skip if tradition exists in merge mode
            if mode == "merge" and Tradition.query.filter_by(name=tradition_data.get('name')).first():
                continue

            try:
                # Create new tradition
                new_tradition = Tradition(
                    name=tradition_data.get('name', ''),
                    start_century=tradition_data.get('start_century', 0),
                    end_century=tradition_data.get('end_century', 0),
                    region=tradition_data.get('region', ''),
                    major_texts=json.dumps(tradition_data.get('major_texts', [])),
                    key_figures=json.dumps(tradition_data.get('key_figures', [])),
                    core_concepts=json.dumps(tradition_data.get('core_concepts', []))
                )
                db.session.add(new_tradition)
                tradition_count += 1
            except Exception as e:
                console.print(f"[red]Error importing tradition {tradition_data.get('name')}: {str(e)}[/red]")

        # Import connections
        connection_count = 0
        for connection_data in import_data['connections']:
            source_id = connection_data.get('source')
            target_id = connection_data.get('target')

            # Skip if connection exists in merge mode
            if mode == "merge" and Connection.query.filter_by(
                    source_id=source_id, target_id=target_id
            ).first():
                continue

            # Check if source and target exist
            source = Symbol.query.get(source_id)
            target = Symbol.query.get(target_id)

            if not source or not target:
                console.print(
                    f"[yellow]Skipping connection {source_id}->{target_id}: Source or target not found[/yellow]")
                continue

            try:
                # Create new connection
                new_connection = Connection(
                    source_id=source_id,
                    target_id=target_id,
                    strength=connection_data.get('strength', 0.5),
                    description=connection_data.get('description', '')
                )
                db.session.add(new_connection)
                connection_count += 1
            except Exception as e:
                console.print(f"[red]Error importing connection {source_id}->{target_id}: {str(e)}[/red]")

        # Commit all changes
        db.session.commit()

        console.print(f"[green]Import completed successfully[/green]")
        console.print(
            f"Imported {symbol_count} symbols, {tradition_count} traditions, and {connection_count} connections")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error importing data: {str(e)}[/red]")


def prune_orphans(args):
    """Find and remove orphaned database entries"""
    console.print(Panel.fit("[bold]Pruning Orphaned Database Entries[/bold]", border_style="yellow"))

    # Find orphaned connections
    orphaned_connections = []
    for connection in Connection.query.all():
        source = Symbol.query.get(connection.source_id)
        target = Symbol.query.get(connection.target_id)

        if not source or not target:
            orphaned_connections.append(connection)

    # Find orphaned elements (elements not associated with any symbol)
    orphaned_elements = []
    if hasattr(Element, 'symbols'):
        for element in Element.query.all():
            if element.symbols.count() == 0:
                orphaned_elements.append(element)

    # Report findings
    console.print(f"Found {len(orphaned_connections)} orphaned connections")
    console.print(f"Found {len(orphaned_elements)} orphaned elements")

    # Ask user what to prune
    prune_connections = len(orphaned_connections) > 0 and Confirm.ask("Prune orphaned connections?")
    prune_elements = len(orphaned_elements) > 0 and Confirm.ask("Prune orphaned elements?")

    if not prune_connections and not prune_elements:
        console.print("[yellow]No pruning selected. Operation cancelled.[/yellow]")
        return

    # Perform pruning
    try:
        if prune_connections:
            for connection in orphaned_connections:
                db.session.delete(connection)

        if prune_elements:
            for element in orphaned_elements:
                db.session.delete(element)

        db.session.commit()

        console.print(f"[green]Pruning completed successfully[/green]")
        console.print(f"Pruned {len(orphaned_connections) if prune_connections else 0} connections and "
                      f"{len(orphaned_elements) if prune_elements else 0} elements")
    except Exception as e:
        db.session.rollback()
        console.print(f"[red]Error pruning database: {str(e)}[/red]")


def stats(args):
    """Display database statistics"""
    console.print(Panel.fit("[bold]Database Statistics[/bold]", border_style="blue"))

    # Get counts
    symbol_count = Symbol.query.count()
    tradition_count = Tradition.query.count()
    connection_count = Connection.query.count()
    element_count = Element.query.count() if hasattr(Element, 'query') else 0

    # Build stats table
    table = Table(title="Database Overview")
    table.add_column("Entity Type", style="cyan")
    table.add_column("Count", justify="right", style="green")

    table.add_row("Symbols", str(symbol_count))
    table.add_row("Traditions", str(tradition_count))
    table.add_row("Connections", str(connection_count))
    table.add_row("Elements", str(element_count))

    console.print(table)

    # Show tradition distribution
    if symbol_count > 0:
        tradition_stats = {}
        for symbol in Symbol.query.all():
            # Handle multi-tradition symbols
            traditions = symbol.tradition.split('/')
            for t in traditions:
                t = t.strip()
                if t in tradition_stats:
                    tradition_stats[t] += 1
                else:
                    tradition_stats[t] = 1

        # Sort by count
        sorted_traditions = sorted(tradition_stats.items(), key=lambda x: x[1], reverse=True)

        table = Table(title="Symbol Distribution by Tradition")
        table.add_column("Tradition", style="blue")
        table.add_column("Symbol Count", justify="right", style="green")
        table.add_column("Percentage", justify="right")

        for tradition, count in sorted_traditions:
            percentage = (count / symbol_count) * 100
            table.add_row(
                tradition,
                str(count),
                f"{percentage:.1f}%"
            )

        console.print(table)


def main():
    """Main entry point for the CLI tool"""
    parser = argparse.ArgumentParser(description="Occult Symbols Database Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List commands
    list_parser = subparsers.add_parser("list", help="List database entries")
    list_subparsers = list_parser.add_subparsers(dest="list_type")

    symbols_parser = list_subparsers.add_parser("symbols", help="List symbols")
    symbols_parser.add_argument("--tradition", help="Filter by tradition")
    symbols_parser.add_argument("--element", help="Filter by element")
    symbols_parser.add_argument("--period", help="Filter by time period (e.g., '5 CE' or '3 BCE')")
    symbols_parser.set_defaults(func=list_symbols)

    traditions_parser = list_subparsers.add_parser("traditions", help="List traditions")
    traditions_parser.set_defaults(func=list_traditions)

    connections_parser = list_subparsers.add_parser("connections", help="List connections")
    connections_parser.set_defaults(func=list_connections)

    # Add commands
    add_parser = subparsers.add_parser("add", help="Add database entries")
    add_subparsers = add_parser.add_subparsers(dest="add_type")

    add_symbol_parser = add_subparsers.add_parser("symbol", help="Add a symbol")
    add_symbol_parser.set_defaults(func=add_symbol)

    add_tradition_parser = add_subparsers.add_parser("tradition", help="Add a tradition")
    add_tradition_parser.set_defaults(func=add_tradition)

    add_connection_parser = add_subparsers.add_parser("connection", help="Add a connection")
    add_connection_parser.set_defaults(func=add_connection)

    # Edit commands
    edit_parser = subparsers.add_parser("edit", help="Edit database entries")
    edit_subparsers = edit_parser.add_subparsers(dest="edit_type")

    edit_symbol_parser = edit_subparsers.add_parser("symbol", help="Edit a symbol")
    edit_symbol_parser.add_argument("--id", type=int, help="Symbol ID to edit")
    edit_symbol_parser.set_defaults(func=edit_symbol)

    edit_tradition_parser = edit_subparsers.add_parser("tradition", help="Edit a tradition")
    edit_tradition_parser.add_argument("--name", help="Tradition name to edit")
    edit_tradition_parser.set_defaults(func=edit_tradition)

    # Delete commands
    delete_parser = subparsers.add_parser("delete", help="Delete database entries")
    delete_subparsers = delete_parser.add_subparsers(dest="delete_type")

    delete_symbol_parser = delete_subparsers.add_parser("symbol", help="Delete a symbol")
    delete_symbol_parser.add_argument("--id", type=int, help="Symbol ID to delete")
    delete_symbol_parser.set_defaults(func=delete_symbol)

    delete_tradition_parser = delete_subparsers.add_parser("tradition", help="Delete a tradition")
    delete_tradition_parser.add_argument("--name", help="Tradition name to delete")
    delete_tradition_parser.set_defaults(func=delete_tradition)

    delete_connection_parser = delete_subparsers.add_parser("connection", help="Delete a connection")
    delete_connection_parser.set_defaults(func=delete_connection)

    # Export/Import commands
    export_parser = subparsers.add_parser("export", help="Export database to JSON")
    export_parser.add_argument("--file", help="Output file path")
    export_parser.set_defaults(func=export_data)

    import_parser = subparsers.add_parser("import", help="Import database from JSON")
    import_parser.add_argument("--file", required=True, help="Input file path")
    import_parser.add_argument("--mode", choices=["merge", "replace"], help="Import mode")
    import_parser.set_defaults(func=import_data)

    # Maintenance commands
    prune_parser = subparsers.add_parser("prune", help="Prune orphaned database entries")
    prune_parser.set_defaults(func=prune_orphans)

    stats_parser = subparsers.add_parser("stats", help="Display database statistics")
    stats_parser.set_defaults(func=stats)

    args = parser.parse_args()

    # Initialize database connection
    app = init_db()

    if hasattr(args, 'func'):
        args.func(args)
    elif args.command == "list":
        console.print("[yellow]Please specify what to list: symbols, traditions, or connections[/yellow]")
    elif args.command == "add":
        console.print("[yellow]Please specify what to add: symbol, tradition, or connection[/yellow]")
    elif args.command == "edit":
        console.print("[yellow]Please specify what to edit: symbol or tradition[/yellow]")
    elif args.command == "delete":
        console.print("[yellow]Please specify what to delete: symbol, tradition, or connection[/yellow]")
    else:
        # Interactive mode if no command is provided
        console.print(Panel.fit("[bold cyan]Occult Symbols Database Manager[/bold cyan]", border_style="green"))
        console.print("Interactive mode - select an action:")

        actions = [
            "List symbols", "List traditions", "List connections",
            "Add symbol", "Add tradition", "Add connection",
            "Edit symbol", "Edit tradition",
            "Delete symbol", "Delete tradition", "Delete connection",
            "Export data", "Import data",
            "Prune orphans", "Show stats",
            "Exit"
        ]

        action = Prompt.ask("[bold]Select action[/bold]", choices=actions)

        if action == "List symbols":
            list_symbols(args)
        elif action == "List traditions":
            list_traditions(args)
        elif action == "List connections":
            list_connections(args)
        elif action == "Add symbol":
            add_symbol(args)
        elif action == "Add tradition":
            add_tradition(args)
        elif action == "Add connection":
            add_connection(args)
        elif action == "Edit symbol":
            edit_symbol(args)
        elif action == "Edit tradition":
            edit_tradition(args)
        elif action == "Delete symbol":
            delete_symbol(args)
        elif action == "Delete tradition":
            delete_tradition(args)
        elif action == "Delete connection":
            delete_connection(args)
        elif action == "Export data":
            file = Prompt.ask("[bold]Output file path[/bold]", default="occult_symbols_export.json")
            args.file = file
            export_data(args)
        elif action == "Import data":
            file = Prompt.ask("[bold]Input file path[/bold]")
            mode = Prompt.ask("[bold]Import mode[/bold]", choices=["merge", "replace"], default="merge")
            args.file = file
            args.mode = mode
            import_data(args)
        elif action == "Prune orphans":
            prune_orphans(args)
        elif action == "Show stats":
            stats(args)
        elif action == "Exit":
            console.print("[green]Goodbye![/green]")


if __name__ == "__main__":
    main()