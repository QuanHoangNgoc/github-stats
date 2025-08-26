import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

# Dummy Stats class (replace with your real implementation)
class Stats:
    async def name(self): return "QuanHoangNgoc"
    async def stargazers(self): return 42
    async def forks(self): return 7
    async def total_contributions(self): return 1234
    async def lines_changed(self): return (500, 200)
    async def views(self): return 256
    async def repos(self): return ["repo1", "repo2"]

def generate_output_folder():
    os.makedirs("generated", exist_ok=True)

async def generate_overview(s: Stats) -> None:
    name = await s.name()
    stars = await s.stargazers()
    forks = await s.forks()
    contributions = await s.total_contributions()
    changed = (await s.lines_changed())[0] + (await s.lines_changed())[1]
    views = await s.views()
    repos = len(await s.repos())

    width, height = 500, 300
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_text = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    draw.text((20, 20), f"{name}'s GitHub Statistics", font=font_title, fill=(0, 0, 0))

    stats = [
        f"⭐ Stars: {stars:,}",
        f"🍴 Forks: {forks:,}",
        f"📝 All-time contributions: {contributions:,}",
        f"🔀 Lines of code changed: {changed:,}",
        f"👀 Repository views (2w): {views:,}",
        f"📦 Repositories with contributions: {repos:,}",
    ]

    y = 60
    for line in stats:
        draw.text((40, y), line, font=font_text, fill=(0, 0, 0))
        y += 30

    generate_output_folder()
    img.save("github-stats.png")   # save to root so Action can commit it

if __name__ == "__main__":
    asyncio.run(generate_overview(Stats()))
