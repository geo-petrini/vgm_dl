from datetime import datetime
import time

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.prompt import IntPrompt
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from  rich.box import *
from rich.live import Live  #https://rich.readthedocs.io/en/stable/live.html#live


###TODO
# include progress for urls
# include controll for title customization
# use live
# use layout
# https://www.freecodecamp.org/news/use-the-rich-library-in-python/
# https://github.com/Textualize/rich/tree/master

console = Console()

def generate_url_table(urls) -> Table:
    table = Table(title="List of URLs", title_justify="left")
    table.add_column("Index", justify="right")
    table.add_column("URL")

    for i, url in enumerate(urls):
        table.add_row(str(i + 1), url)

    # console.print(table)
    return table

def create_main_panel(jobs: list) -> Panel:
    url_table = Table(title="Jobs", title_justify="left")
    url_table.add_column("Index", justify="right")
    url_table.add_column("URL")  

    for i, job in enumerate(jobs):
        url_table.add_row(str(i + 1), job)

    main = Panel(
        url_table,
        title = 'URLs',
        style="green on black",
        box = ROUNDED
    )

    return main
 
def create_layout() -> Layout:
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=2)
    )

    return layout

class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "[b]V[/b]ideo [b]G[/b]ame [b]M[/b]usic [b]D[/b]ownloader",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on blue")

class Job(Progress):

    def __init__(self, text:str, color:str = None):
        super().__init__(
            "{task.description}",
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        description = f'[{color}]{text}' if color else text
        self.add_task(description, total = 100)

def main():
    jobs = [Job('j1'), Job('j2'), Job('https://downloads.khinsider.com/game-soundtracks/album/castlevania-symphony-of-the-night')]
    lyt = create_layout()

    lyt["header"].update(Header())
    lyt["main"].update(create_main_panel(jobs))

    overall_progress = Progress()
    finished = False
    with Live(lyt, refresh_per_second=10, screen=True):
        while not finished:
            time.sleep(0.1)
            completed = 0
            for job in jobs:
                job.advance(0)
                completed += sum(task.completed for task in job.tasks)

            if completed == len(jobs) * 100:
                finished = True

if __name__ == "__main__":
    main()
