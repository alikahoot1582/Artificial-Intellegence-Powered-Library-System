"""
📚 AI-Powered Library — Streamlit Agentic App
Uses Google Gemini + Open Library API + Project Gutenberg to search, retrieve, and manage books.
Features: SQLite persistence, reading progress, ratings, full book content from Gutenberg.
"""

import streamlit as st
import requests
import json
import sqlite3
import os
from datetime import datetime
from google import genai
from google.genai import types as genai_types

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Library • AI Powered",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,400&display=swap');

:root {
    --ink: #1a1008;
    --parchment: #f8f3e8;
    --gold: #c9922a;
    --sienna: #8b4513;
    --muted: #6b5a45;
    --card-bg: #fdf8ef;
    --border: #d4c4a0;
    --green: #2d6a2d;
}

html, body, [class*="css"] {
    font-family: 'Crimson Pro', Georgia, serif;
    background-color: var(--parchment);
    color: var(--ink);
}
h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif; color: var(--ink); }
.stApp { background: linear-gradient(135deg, #f8f3e8 0%, #f0e8d5 100%); }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2c1a0e 0%, #1a0f06 100%) !important;
    border-right: 2px solid var(--gold);
}
section[data-testid="stSidebar"] * { color: #f0e0c0 !important; }
section[data-testid="stSidebar"] h2 { color: var(--gold) !important; font-family: 'Playfair Display', serif !important; }

.user-msg {
    background: linear-gradient(135deg, #4a2c0e, #2c1a0a);
    color: #f0ddb8;
    padding: 14px 18px;
    border-radius: 16px 16px 4px 16px;
    margin: 8px 0;
    border-left: 3px solid var(--gold);
    font-size: 1.05rem;
    line-height: 1.6;
}
.assistant-msg {
    background: var(--card-bg);
    color: var(--ink);
    padding: 14px 18px;
    border-radius: 16px 16px 16px 4px;
    margin: 8px 0;
    border-left: 3px solid var(--sienna);
    font-size: 1.05rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.tool-call {
    background: #2c1a0e;
    color: #a0c878;
    padding: 8px 14px;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    margin: 4px 0;
    border: 1px solid #3a2a18;
}
.book-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
    box-shadow: 0 3px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    overflow: hidden;
}
.book-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
.book-title { font-family: 'Playfair Display', serif; font-size: 1.3rem; color: var(--ink); font-weight: 700; }
.book-author { color: var(--sienna); font-size: 1rem; font-style: italic; }
.book-meta { color: var(--muted); font-size: 0.9rem; margin-top: 6px; }
.book-badge {
    display: inline-block;
    background: var(--gold);
    color: #fff;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 12px;
    font-weight: 600;
    margin-right: 4px;
}
.badge-personal { background: var(--sienna); }
.badge-reading { background: #1a6b8a; }
.badge-done { background: var(--green); }
.badge-ebook { background: #1a6b3a; }

.progress-bar-bg {
    background: #e8d5b0;
    border-radius: 8px;
    height: 8px;
    margin-top: 8px;
    overflow: hidden;
}
.progress-bar-fill {
    height: 8px;
    border-radius: 8px;
    background: linear-gradient(90deg, var(--sienna), var(--gold));
}
.stars { color: var(--gold); font-size: 1.1rem; letter-spacing: 2px; }
.stars-empty { color: #c8b890; }

.app-header {
    text-align: center;
    padding: 20px 0 10px;
    border-bottom: 2px solid var(--border);
    margin-bottom: 24px;
}
.app-title { font-family: 'Playfair Display', serif; font-size: 2.8rem; color: var(--ink); letter-spacing: 0.02em; }
.app-subtitle { color: var(--muted); font-size: 1.1rem; font-style: italic; }

.stButton > button {
    background: linear-gradient(135deg, #8b4513, #c9922a) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Crimson Pro', serif !important;
    font-size: 1rem !important;
    padding: 8px 20px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

.stTextInput input, .stTextArea textarea {
    background: #fdf8ef !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Crimson Pro', serif !important;
    font-size: 1rem !important;
    color: var(--ink) !important;
}
.status-box {
    background: linear-gradient(135deg, #fff9ee, #fdf3dd);
    border: 1px solid #e8d5a0;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.95rem;
}
.reading-content {
    background: #fefcf5;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 32px 40px;
    font-family: 'Crimson Pro', Georgia, serif;
    font-size: 1.15rem;
    line-height: 1.9;
    color: #1a1008;
    max-height: 600px;
    overflow-y: auto;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.04);
    white-space: pre-wrap;
}
.stat-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stat-number { font-family: 'Playfair Display', serif; font-size: 2.2rem; color: var(--sienna); font-weight: 700; }
.stat-label { color: var(--muted); font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ─── SQLite Database ─────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            year INTEGER,
            isbn TEXT DEFAULT '',
            cover_url TEXT DEFAULT '',
            open_library_key TEXT DEFAULT '',
            gutenberg_id INTEGER,
            source TEXT DEFAULT 'Personal',
            added_at TEXT NOT NULL,
            status TEXT DEFAULT 'unread',
            rating INTEGER DEFAULT 0,
            review TEXT DEFAULT '',
            current_page INTEGER DEFAULT 0,
            total_pages INTEGER DEFAULT 0,
            started_at TEXT,
            finished_at TEXT
        );
    """)
    conn.commit()
    conn.close()

init_db()

def db_load_library():
    conn = get_db()
    rows = conn.execute("SELECT * FROM books ORDER BY added_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_add_book(title, author, genre="", notes="", year=None, isbn="", cover_url="",
                open_library_key="", gutenberg_id=None, total_pages=0):
    conn = get_db()
    conn.execute("""
        INSERT INTO books (title, author, genre, notes, year, isbn, cover_url,
        open_library_key, gutenberg_id, source, added_at, total_pages)
        VALUES (?,?,?,?,?,?,?,?,?,'Personal',?,?)
    """, (title, author, genre, notes, year, isbn, cover_url,
          open_library_key, gutenberg_id,
          datetime.now().strftime("%Y-%m-%d"), total_pages or 0))
    conn.commit()
    book_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return book_id

def db_update_progress(book_id, current_page=None, total_pages=None,
                        status=None, rating=None, review=None):
    updates, values = [], []
    if current_page is not None:
        updates.append("current_page=?"); values.append(current_page)
    if total_pages is not None:
        updates.append("total_pages=?"); values.append(total_pages)
    if status is not None:
        updates.append("status=?"); values.append(status)
        if status == "reading":
            updates.append("started_at=?"); values.append(datetime.now().strftime("%Y-%m-%d"))
        elif status == "finished":
            updates.append("finished_at=?"); values.append(datetime.now().strftime("%Y-%m-%d"))
    if rating is not None:
        updates.append("rating=?"); values.append(max(0, min(5, int(rating))))
    if review is not None:
        updates.append("review=?"); values.append(review)
    if not updates:
        return False
    values.append(book_id)
    conn = get_db()
    conn.execute(f"UPDATE books SET {', '.join(updates)} WHERE id=?", values)
    conn.commit()
    conn.close()
    return True

def db_remove_book(book_id):
    conn = get_db()
    c = conn.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0

def db_get_book(book_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def sync_library():
    st.session_state.personal_library = db_load_library()

# ─── Anthropic Client ────────────────────────────────────────────────────────
# NOTE: Do NOT cache — key changes at runtime.
def get_client():
    api_key = st.session_state.get("anthropic_api_key", "").strip()
    if api_key:
        return genai.Client(api_key=api_key)
    return None


def _build_gemini_tools():
    """Convert tool definitions into new google-genai SDK FunctionDeclaration format."""
    TYPE_MAP = {
        "string": genai_types.Type.STRING,
        "integer": genai_types.Type.INTEGER,
        "number": genai_types.Type.NUMBER,
        "boolean": genai_types.Type.BOOLEAN,
        "array": genai_types.Type.ARRAY,
        "object": genai_types.Type.OBJECT,
    }

    def build_schema(pval):
        ptype = TYPE_MAP.get(str(pval.get("type", "string")).lower(), genai_types.Type.STRING)
        kwargs = {"type": ptype}
        if "description" in pval:
            kwargs["description"] = pval["description"]
        if "enum" in pval:
            kwargs["enum"] = [str(e) for e in pval["enum"] if e]
        return genai_types.Schema(**kwargs)

    declarations = []
    for t in TOOLS:
        schema = t["input_schema"]
        props = {}
        for pname, pval in schema.get("properties", {}).items():
            props[pname] = build_schema(pval)
        required = schema.get("required", [])
        param_schema = genai_types.Schema(
            type=genai_types.Type.OBJECT,
            properties=props,
            required=required,
        )
        declarations.append(genai_types.FunctionDeclaration(
            name=t["name"],
            description=t["description"],
            parameters=param_schema,
        ))
    return [genai_types.Tool(function_declarations=declarations)]

# ─── Session State ───────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [],
        "personal_library": [],
        "anthropic_api_key": "",
        "page": "Chat",
        "reading_book_id": None,
        "reading_content": "",
        "reading_offset": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
sync_library()

# ─── Tool Functions ───────────────────────────────────────────────────────────

def search_open_library(query: str, limit: int = 8) -> dict:
    try:
        params = {"q": query, "limit": limit,
                  "fields": "key,title,author_name,first_publish_year,number_of_pages_median,subject,isbn,cover_i,publisher"}
        r = requests.get("https://openlibrary.org/search.json", params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        books = []
        for doc in data.get("docs", []):
            books.append({
                "title": doc.get("title", "Unknown"),
                "authors": doc.get("author_name", ["Unknown"]),
                "year": doc.get("first_publish_year"),
                "pages": doc.get("number_of_pages_median"),
                "subjects": doc.get("subject", [])[:5],
                "isbn": (doc.get("isbn") or [None])[0],
                "cover_id": doc.get("cover_i"),
                "publisher": (doc.get("publisher") or [None])[0],
                "open_library_key": doc.get("key"),
                "source": "Open Library",
            })
        return {"success": True, "total": data.get("numFound", 0), "books": books}
    except Exception as e:
        return {"success": False, "error": str(e), "books": []}


def get_book_details(open_library_key: str) -> dict:
    try:
        r = requests.get(f"https://openlibrary.org{open_library_key}.json", timeout=10)
        r.raise_for_status()
        data = r.json()
        description = data.get("description")
        if isinstance(description, dict):
            description = description.get("value", "")
        return {
            "success": True,
            "title": data.get("title"),
            "description": description or "No description available.",
            "subjects": data.get("subjects", [])[:10],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_gutenberg(query: str, limit: int = 8) -> dict:
    try:
        r = requests.get("https://gutendex.com/books/",
                         params={"search": query, "mime_type": "text/plain"}, timeout=12)
        r.raise_for_status()
        data = r.json()
        books = []
        for item in data.get("results", [])[:limit]:
            fmts = item.get("formats", {})
            txt_url = (fmts.get("text/plain; charset=utf-8") or
                       fmts.get("text/plain; charset=us-ascii") or
                       fmts.get("text/plain"))
            books.append({
                "gutenberg_id": item["id"],
                "title": item.get("title", "Unknown"),
                "authors": [a.get("name", "Unknown") for a in item.get("authors", [])],
                "subjects": item.get("subjects", [])[:5],
                "download_count": item.get("download_count", 0),
                "txt_url": txt_url,
                "cover_url": fmts.get("image/jpeg", ""),
            })
        return {"success": True, "total": data.get("count", 0), "books": books}
    except Exception as e:
        return {"success": False, "error": str(e), "books": []}


def fetch_gutenberg_content(gutenberg_id: int, offset: int = 0, chunk_size: int = 3000) -> dict:
    try:
        r = requests.get(f"https://gutendex.com/books/{gutenberg_id}/", timeout=10)
        r.raise_for_status()
        data = r.json()
        fmts = data.get("formats", {})
        txt_url = (fmts.get("text/plain; charset=utf-8") or
                   fmts.get("text/plain; charset=us-ascii") or
                   fmts.get("text/plain"))
        if not txt_url:
            return {"success": False, "error": "No plain text version available."}
        byte_end = offset + chunk_size * 4
        r2 = requests.get(txt_url, headers={"Range": f"bytes={offset}-{byte_end}"}, timeout=15)
        content = r2.content.decode("utf-8", errors="replace")
        if len(content) > chunk_size:
            content = content[:chunk_size].rsplit(" ", 1)[0]
        return {
            "success": True,
            "gutenberg_id": gutenberg_id,
            "title": data.get("title"),
            "authors": [a.get("name") for a in data.get("authors", [])],
            "content": content,
            "offset": offset,
            "next_offset": offset + chunk_size * 4,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_to_personal_library(title: str, author: str, genre: str = "", notes: str = "",
                             year: int = None, isbn: str = "", gutenberg_id: int = None,
                             open_library_key: str = "", total_pages: int = 0) -> dict:
    book_id = db_add_book(title, author, genre, notes, year, isbn, "",
                          open_library_key, gutenberg_id, total_pages)
    sync_library()
    return {
        "success": True,
        "message": f"'{title}' by {author} added (ID #{book_id})." +
                   (" 📖 Free eBook available via Gutenberg!" if gutenberg_id else ""),
        "book_id": book_id,
    }


def list_personal_library(genre_filter: str = "", search_query: str = "",
                           status_filter: str = "") -> dict:
    books = db_load_library()
    if genre_filter:
        books = [b for b in books if genre_filter.lower() in b.get("genre", "").lower()]
    if search_query:
        sq = search_query.lower()
        books = [b for b in books if sq in b["title"].lower() or sq in b["author"].lower()]
    if status_filter:
        books = [b for b in books if b.get("status") == status_filter]
    return {"success": True, "count": len(books), "books": books}


def remove_from_library(book_id: int) -> dict:
    ok = db_remove_book(book_id)
    sync_library()
    return {"success": ok, "message": f"Book #{book_id} {'removed' if ok else 'not found'}."}


def update_reading_progress(book_id: int, current_page: int = None, total_pages: int = None,
                             status: str = None, rating: int = None, review: str = None) -> dict:
    ok = db_update_progress(book_id, current_page, total_pages, status, rating, review)
    sync_library()
    if ok:
        parts = []
        if current_page is not None: parts.append(f"page→{current_page}")
        if status: parts.append(f"status→{status}")
        if rating is not None: parts.append(f"rating→{'★'*rating}")
        if review: parts.append("review saved")
        return {"success": True, "message": f"Book #{book_id} updated: {', '.join(parts) or 'saved'}."}
    return {"success": False, "message": f"Book #{book_id} not found."}


def get_recommendations(genre: str = "", mood: str = "", based_on: str = "") -> dict:
    personal = db_load_library()
    return {
        "success": True,
        "personal_library_count": len(personal),
        "personal_titles": [b["title"] for b in personal[:10]],
        "personal_genres": list(set(b.get("genre","") for b in personal if b.get("genre"))),
        "recently_finished": [b["title"] for b in personal if b.get("status")=="finished"][:5],
        "currently_reading": [b["title"] for b in personal if b.get("status")=="reading"][:3],
        "request": {"genre": genre, "mood": mood, "based_on": based_on},
    }


TOOLS = [
    {
        "name": "search_open_library",
        "description": "Search millions of books from Open Library (internet). Use for any book by title, author, subject, or keyword.",
        "input_schema": {"type": "object",
                         "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 8}},
                         "required": ["query"]},
    },
    {
        "name": "get_book_details",
        "description": "Get detailed description and subjects for a book via its Open Library key.",
        "input_schema": {"type": "object",
                         "properties": {"open_library_key": {"type": "string"}},
                         "required": ["open_library_key"]},
    },
    {
        "name": "search_gutenberg",
        "description": "Search Project Gutenberg for FREE books that can be fully read. Best for classics.",
        "input_schema": {"type": "object",
                         "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 6}},
                         "required": ["query"]},
    },
    {
        "name": "fetch_gutenberg_content",
        "description": "Fetch readable text from a Gutenberg book. Returns a chunk of the actual book content.",
        "input_schema": {"type": "object",
                         "properties": {"gutenberg_id": {"type": "integer"}, "offset": {"type": "integer", "default": 0}},
                         "required": ["gutenberg_id"]},
    },
    {
        "name": "add_to_personal_library",
        "description": "Add a book to the user's personal library. Include gutenberg_id when available.",
        "input_schema": {"type": "object",
                         "properties": {
                             "title": {"type": "string"}, "author": {"type": "string"},
                             "genre": {"type": "string"}, "notes": {"type": "string"},
                             "year": {"type": "integer"}, "isbn": {"type": "string"},
                             "gutenberg_id": {"type": "integer"}, "open_library_key": {"type": "string"},
                             "total_pages": {"type": "integer"},
                         },
                         "required": ["title", "author"]},
    },
    {
        "name": "list_personal_library",
        "description": "List books in the user's personal library with optional filters.",
        "input_schema": {"type": "object",
                         "properties": {
                             "genre_filter": {"type": "string"},
                             "search_query": {"type": "string"},
                             "status_filter": {"type": "string", "enum": ["unread","reading","finished",""]},
                         }},
    },
    {
        "name": "remove_from_library",
        "description": "Remove a book from the personal library by ID.",
        "input_schema": {"type": "object",
                         "properties": {"book_id": {"type": "integer"}},
                         "required": ["book_id"]},
    },
    {
        "name": "update_reading_progress",
        "description": "Update reading status (unread/reading/finished), current page, total pages, star rating (1-5), or review for a book.",
        "input_schema": {"type": "object",
                         "properties": {
                             "book_id": {"type": "integer"},
                             "current_page": {"type": "integer"},
                             "total_pages": {"type": "integer"},
                             "status": {"type": "string", "enum": ["unread","reading","finished"]},
                             "rating": {"type": "integer", "description": "1-5 stars"},
                             "review": {"type": "string"},
                         },
                         "required": ["book_id"]},
    },
    {
        "name": "get_recommendations",
        "description": "Get personalized recommendation context based on library and preferences.",
        "input_schema": {"type": "object",
                         "properties": {
                             "genre": {"type": "string"},
                             "mood": {"type": "string"},
                             "based_on": {"type": "string"},
                         }},
    },
]

TOOL_MAP = {
    "search_open_library": search_open_library,
    "get_book_details": get_book_details,
    "search_gutenberg": search_gutenberg,
    "fetch_gutenberg_content": fetch_gutenberg_content,
    "add_to_personal_library": add_to_personal_library,
    "list_personal_library": list_personal_library,
    "remove_from_library": remove_from_library,
    "update_reading_progress": update_reading_progress,
    "get_recommendations": get_recommendations,
}

# ─── Agentic Loop ────────────────────────────────────────────────────────────
def run_agent(user_message: str):
    client = get_client()
    if not client:
        yield ("error", "⚠️ Please enter your Gemini API key in the sidebar.")
        return

    system_prompt = """You are a knowledgeable and passionate library assistant AI. You help users discover, manage, and READ books.

You have access to:
1. Open Library API — search millions of real books from the internet
2. Project Gutenberg — search and fetch full text of thousands of FREE classic books
3. Personal Library — the user's own collection with persistent reading progress and ratings

Guidelines:
- Search Open Library AND Gutenberg (for classics) when asked about books
- If a Gutenberg book is found, always mention they can read it for free
- When adding books found on Gutenberg, always include the gutenberg_id
- Use update_reading_progress to log status, pages, ratings and reviews
- When someone wants to read, use fetch_gutenberg_content
- Be warm, literary, and enthusiastic. Recommend related books proactively.
"""

    # Build message history for the new SDK format
    history = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        history.append(genai_types.Content(role=role, parts=[genai_types.Part(text=m["content"])]))

    st.session_state.messages.append({"role": "user", "content": user_message})

    gemini_tools = _build_gemini_tools()
    config = genai_types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=gemini_tools,
    )

    try:
        # Start with full history + new user message
        contents = history + [genai_types.Content(role="user", parts=[genai_types.Part(text=user_message)])]

        while True:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=config,
            )

            candidate = response.candidates[0]
            fn_calls = []
            text_parts = []

            for part in candidate.content.parts:
                if part.function_call:
                    fn_calls.append(part.function_call)
                elif part.text:
                    text_parts.append(part.text)

            if text_parts:
                yield ("text", "\n".join(text_parts))

            # No tool calls — done
            if not fn_calls:
                if text_parts:
                    st.session_state.messages.append({"role": "assistant", "content": "\n".join(text_parts)})
                break

            # Append model response to contents
            contents.append(candidate.content)

            # Execute tools and build function response parts
            fn_response_parts = []
            for fc in fn_calls:
                fn_name = fc.name
                fn_args = dict(fc.args) if fc.args else {}
                yield ("tool_call", f"🔧 {fn_name}({str(fn_args)[:80]}...)")
                fn = TOOL_MAP.get(fn_name)
                result = fn(**fn_args) if fn else {"error": f"Unknown tool: {fn_name}"}
                yield ("tool_result", f"✅ {fn_name} → {len(str(result))} chars")
                fn_response_parts.append(
                    genai_types.Part(
                        function_response=genai_types.FunctionResponse(
                            name=fn_name,
                            response={"result": json.dumps(result)},
                        )
                    )
                )

            # Append tool results as a user turn
            contents.append(genai_types.Content(role="user", parts=fn_response_parts))

    except Exception as e:
        err_str = str(e)
        # Roll back the user message on failure
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            st.session_state.messages.pop()
        if "API_KEY_INVALID" in err_str or ("invalid" in err_str.lower() and "key" in err_str.lower()):
            yield ("error", "🔑 **Invalid API key.** Check the key in the sidebar. Get yours at https://aistudio.google.com/apikey")
        elif "PERMISSION_DENIED" in err_str or "403" in err_str:
            yield ("error", "🚫 **Permission denied.** Your key may not have access to this model.")
        elif "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
            yield ("error", "⏳ **Rate limit reached.** Please wait a moment and try again.")
        elif "Connection" in err_str or "network" in err_str.lower():
            yield ("error", "🌐 **Network error.** Check your internet connection and try again.")
        else:
            yield ("error", f"❌ **API error:** {err_str[:300]}")


# ─── UI Helpers ──────────────────────────────────────────────────────────────
def render_stars(rating, max_stars=5):
    return (f"<span class='stars'>{'★' * rating}</span>"
            f"<span class='stars-empty'>{'☆' * (max_stars - rating)}</span>")

def render_progress_bar(current, total):
    if not total:
        return ""
    pct = min(100, int((current or 0) / total * 100))
    return (f"<div class='progress-bar-bg'><div class='progress-bar-fill' style='width:{pct}%'></div></div>"
            f"<div class='book-meta'>{pct}% — page {current or 0} of {total}</div>")

def status_badge(status):
    m = {"reading": ("badge-reading","📖 Reading"), "finished": ("badge-done","✅ Finished"), "unread": ("","📚 Unread")}
    cls, label = m.get(status, ("", status))
    return f"<span class='book-badge {cls}'>{label}</span>"


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 The Library")
    st.markdown("---")

    api_key = st.text_input("Gemini API Key", type="password",
                             value=st.session_state.anthropic_api_key, placeholder="AIza...")
    if api_key != st.session_state.anthropic_api_key:
        st.session_state.anthropic_api_key = api_key.strip()

    if st.session_state.anthropic_api_key:
        if len(st.session_state.anthropic_api_key) > 20:
            st.markdown("<div style=\'color:#7fc97f;font-size:0.85rem\'>✅ API key set</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style=\'color:#e07070;font-size:0.85rem\'>⚠️ Key looks too short — check it</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style=\'color:#e0b870;font-size:0.85rem\'>🔑 Enter key to use AI Chat</div>", unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio("Navigate", ["💬 Chat", "📖 My Library", "🔍 Quick Search", "📑 Read a Book", "📊 Stats"], key="nav")
    st.session_state.page = page.split(" ", 1)[1]

    st.markdown("---")
    lib = st.session_state.personal_library
    st.markdown(f"**Collection:** {len(lib)} books")
    rc = sum(1 for b in lib if b.get("status") == "reading")
    fc = sum(1 for b in lib if b.get("status") == "finished")
    if rc: st.markdown(f"📖 {rc} currently reading")
    if fc: st.markdown(f"✅ {fc} finished")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("""
<div style='font-size:0.82rem; color:#a08060; line-height:1.7'>
<b>Try asking:</b><br>
• "Find free classics by Dickens"<br>
• "Add Dune to my library"<br>
• "Mark book #1 finished, 5 stars"<br>
• "Read me Pride and Prejudice"<br>
• "What am I reading now?"<br>
• "Recommend something adventurous"
</div>""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class='app-header'>
    <div class='app-title'>📚 The Library</div>
    <div class='app-subtitle'>AI-Powered Book Discovery, Management & Reading</div>
</div>""", unsafe_allow_html=True)

current_page = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════════
# CHAT
# ══════════════════════════════════════════════════════════════════════════════
if current_page == "Chat":
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"<div class='assistant-msg'>📚 {msg['content']}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input("Ask the librarian...",
                                   placeholder="Search books, update progress, get recommendations...",
                                   label_visibility="collapsed", key="chat_input")
    with col2:
        send = st.button("Send →", use_container_width=True)

    qcols = st.columns(4)
    quick = ["📚 Recommend me a book", "🆓 Free classics to read", "📖 Show my library", "✨ Surprise me!"]
    for i, (col, action) in enumerate(zip(qcols, quick)):
        with col:
            if st.button(action, key=f"qa_{i}", use_container_width=True):
                user_input = action; send = True

    if send and user_input:
        st.markdown(f"<div class='user-msg'>🧑 {user_input}</div>", unsafe_allow_html=True)
        rp = st.empty()
        tc = st.container()
        full = ""
        with st.spinner("The librarian is thinking..."):
            for etype, content in run_agent(user_input):
                if etype == "text":
                    full += content
                    rp.markdown(f"<div class='assistant-msg'>📚 {full}</div>", unsafe_allow_html=True)
                elif etype in ("tool_call", "tool_result"):
                    with tc:
                        st.markdown(f"<div class='tool-call'>{content}</div>", unsafe_allow_html=True)
                elif etype == "error":
                    st.error(content)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MY LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
elif current_page == "My Library":
    st.markdown("### 📖 Your Personal Collection")
    library = st.session_state.personal_library

    if not library:
        st.markdown("""<div class='status-box'>
<b>Your library is empty.</b> Use Chat to ask the AI to add books, Quick Search, or the form below.
</div>""", unsafe_allow_html=True)
    else:
        f1, f2, f3 = st.columns([3, 1, 1])
        with f1:
            search = st.text_input("Search", placeholder="Title or author...", label_visibility="collapsed")
        with f2:
            genres = list(set(b.get("genre","") for b in library if b.get("genre")))
            gf = st.selectbox("Genre", ["All"] + sorted(genres), label_visibility="collapsed")
        with f3:
            sf = st.selectbox("Status", ["All","unread","reading","finished"], label_visibility="collapsed")

        books = library
        if search:
            sq = search.lower()
            books = [b for b in books if sq in b["title"].lower() or sq in b["author"].lower()]
        if gf != "All":
            books = [b for b in books if b.get("genre","") == gf]
        if sf != "All":
            books = [b for b in books if b.get("status") == sf]

        st.markdown(f"**{len(books)} book{'s' if len(books)!=1 else ''}**")

        for book in books:
            c1, c2, c3 = st.columns([5, 1, 1])
            with c1:
                gbadge = f"<span class='book-badge badge-personal'>{book.get('genre','')}</span>" if book.get("genre") else ""
                ebook_badge = "<span class='book-badge badge-ebook'>📖 Free eBook</span>" if book.get("gutenberg_id") else ""
                yr = f" • {book['year']}" if book.get("year") else ""
                notes_h = f"<div class='book-meta' style='font-style:italic;margin-top:4px'>📝 {book['notes']}</div>" if book.get("notes") else ""
                review_h = f"<div class='book-meta' style='font-style:italic;margin-top:4px'>💬 {book['review']}</div>" if book.get("review") else ""
                stars_h = render_stars(book.get("rating",0)) if book.get("rating") else ""
                prog_h = render_progress_bar(book.get("current_page",0), book.get("total_pages",0)) if book.get("total_pages") else ""

                st.markdown(f"""
<div class='book-card'>
    <div class='book-title'>{book['title']}</div>
    <div class='book-author'>by {book['author']}{yr}</div>
    <div class='book-meta' style='margin-top:6px'>
        {gbadge}{status_badge(book.get('status','unread'))}{ebook_badge}
        {" • Added "+book['added_at'] if book.get('added_at') else ""}
        {" • Started "+book['started_at'] if book.get('started_at') else ""}
        {" • Finished "+book['finished_at'] if book.get('finished_at') else ""}
    </div>
    {stars_h}{prog_h}{notes_h}{review_h}
    <div class='book-meta' style='margin-top:6px;color:#9b8060'>ID: #{book['id']}</div>
</div>""", unsafe_allow_html=True)
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if book.get("gutenberg_id"):
                    if st.button("📖 Read", key=f"read_{book['id']}"):
                        st.session_state.reading_book_id = book["id"]
                        st.session_state.reading_content = ""
                        st.session_state.reading_offset = 0
                        st.session_state.page = "Read a Book"
                        st.rerun()
            with c3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{book['id']}", help="Remove"):
                    db_remove_book(book["id"]); sync_library(); st.rerun()

            with st.expander(f"✏️ Edit progress & rating — {book['title'][:40]}"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    new_status = st.selectbox("Status", ["unread","reading","finished"],
                                              index=["unread","reading","finished"].index(book.get("status","unread")),
                                              key=f"st_{book['id']}")
                with ec2:
                    cpg = st.number_input("Current page", min_value=0, value=book.get("current_page",0) or 0, key=f"cp_{book['id']}")
                    tpg = st.number_input("Total pages", min_value=0, value=book.get("total_pages",0) or 0, key=f"tp_{book['id']}")
                with ec3:
                    nrat = st.slider("Rating ★", 0, 5, value=book.get("rating",0) or 0, key=f"r_{book['id']}")
                nrev = st.text_area("Review", value=book.get("review","") or "", key=f"rv_{book['id']}", height=60)
                if st.button("💾 Save", key=f"sv_{book['id']}"):
                    db_update_progress(book["id"], cpg or None, tpg or None, new_status, nrat or None, nrev or None)
                    sync_library(); st.success("Saved!"); st.rerun()

    st.markdown("---")
    with st.expander("➕ Add a Book Manually"):
        c1, c2 = st.columns(2)
        with c1:
            mt = st.text_input("Title *"); ma = st.text_input("Author *")
            mg = st.text_input("Genre"); mgid = st.number_input("Gutenberg ID (optional)", min_value=0, value=0)
        with c2:
            myr = st.number_input("Year", min_value=0, max_value=2100, value=0)
            misbn = st.text_input("ISBN"); mpg = st.number_input("Total pages", min_value=0, value=0)
            mn = st.text_area("Notes", height=68)
        if st.button("Add Book"):
            if mt and ma:
                db_add_book(mt, ma, mg, mn, int(myr) if myr else None, misbn, "",
                            "", int(mgid) if mgid else None, int(mpg) if mpg else 0)
                sync_library(); st.success(f"✅ '{mt}' added!"); st.rerun()
            else:
                st.error("Title and author are required.")

# ══════════════════════════════════════════════════════════════════════════════
# QUICK SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif current_page == "Quick Search":
    tab1, tab2 = st.tabs(["🌐 Open Library", "📗 Project Gutenberg (Free)"])

    with tab1:
        st.markdown("Search millions of books from Open Library.")
        sc, bc = st.columns([5, 1])
        with sc:
            q = st.text_input("Search Open Library", placeholder="Author, title, subject...", label_visibility="collapsed", key="ol_q")
        with bc:
            do_ol = st.button("Search", key="ol_go", use_container_width=True)
        if do_ol and q:
            with st.spinner("Searching..."):
                res = search_open_library(q, 12)
            if res["success"]:
                st.markdown(f"**{res['total']:,} results** — top {len(res['books'])}")
                for book in res["books"]:
                    authors = ", ".join(book["authors"][:2]) if book["authors"] else "Unknown"
                    yr = f" ({book['year']})" if book.get("year") else ""
                    pgs = f" • {book['pages']} pages" if book.get("pages") else ""
                    subj = ", ".join(book["subjects"][:3]) if book.get("subjects") else ""
                    cov = (f"<img src='https://covers.openlibrary.org/b/id/{book['cover_id']}-M.jpg' "
                           f"style='width:55px;height:75px;object-fit:cover;border-radius:4px;float:left;margin-right:14px'/>"
                           if book.get("cover_id") else "")
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.markdown(f"""
<div class='book-card'>{cov}
    <div><div class='book-title'>{book['title']}</div>
    <div class='book-author'>by {authors}{yr}</div>
    <div class='book-meta'><span class='book-badge'>Open Library</span>{pgs}</div>
    {"<div class='book-meta'>🏷️ "+subj+"</div>" if subj else ""}
    </div></div>""", unsafe_allow_html=True)
                    with c2:
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        if st.button("+ Add", key=f"oladd_{book.get('isbn','')}{book['title'][:8]}"):
                            db_add_book(book["title"], ", ".join(book["authors"][:2]),
                                        subj.split(",")[0].strip() if subj else "",
                                        "", book.get("year"), book.get("isbn") or "")
                            sync_library(); st.success("Added!")
            else:
                st.error(res.get("error"))

    with tab2:
        st.markdown("Search thousands of **free** books from Project Gutenberg — readable right inside the app!")
        sc2, bc2 = st.columns([5, 1])
        with sc2:
            gq = st.text_input("Search Gutenberg", placeholder="e.g. Jane Austen, Sherlock Holmes, Moby Dick...", label_visibility="collapsed", key="gut_q")
        with bc2:
            do_gut = st.button("Search", key="gut_go", use_container_width=True)
        if do_gut and gq:
            with st.spinner("Searching Gutenberg..."):
                gres = search_gutenberg(gq, 10)
            if gres["success"]:
                st.markdown(f"**{gres['total']:,} free books** — top {len(gres['books'])}")
                for book in gres["books"]:
                    authors = ", ".join(book["authors"]) if book["authors"] else "Unknown"
                    subj = ", ".join(book["subjects"][:3]) if book.get("subjects") else ""
                    cov = (f"<img src='{book['cover_url']}' style='width:55px;height:75px;object-fit:cover;border-radius:4px;float:left;margin-right:14px'/>"
                           if book.get("cover_url") else "")
                    c1, c2, c3 = st.columns([4, 1, 1])
                    with c1:
                        st.markdown(f"""
<div class='book-card'>{cov}
    <div><div class='book-title'>{book['title']}</div>
    <div class='book-author'>by {authors}</div>
    <div class='book-meta'>
        <span class='book-badge badge-ebook'>📖 Free eBook</span>
        <span class='book-badge'>ID #{book['gutenberg_id']}</span>
        ⬇️ {book['download_count']:,}
    </div>
    {"<div class='book-meta'>🏷️ "+subj+"</div>" if subj else ""}
    </div></div>""", unsafe_allow_html=True)
                    with c2:
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        if st.button("+ Add", key=f"gadd_{book['gutenberg_id']}"):
                            db_add_book(book["title"], authors,
                                        subj.split(",")[0].strip() if subj else "",
                                        "", None, "", book.get("cover_url",""), "", book["gutenberg_id"])
                            sync_library(); st.success("Added!")
                    with c3:
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        if st.button("📖 Read", key=f"gread_{book['gutenberg_id']}"):
                            existing = [b for b in db_load_library() if b.get("gutenberg_id") == book["gutenberg_id"]]
                            if not existing:
                                nid = db_add_book(book["title"], authors, "", "", None, "",
                                                  book.get("cover_url",""), "", book["gutenberg_id"])
                                sync_library()
                                st.session_state.reading_book_id = nid
                            else:
                                st.session_state.reading_book_id = existing[0]["id"]
                            st.session_state.reading_content = ""
                            st.session_state.reading_offset = 0
                            st.session_state.page = "Read a Book"
                            st.rerun()
            else:
                st.error(gres.get("error"))

# ══════════════════════════════════════════════════════════════════════════════
# READ A BOOK
# ══════════════════════════════════════════════════════════════════════════════
elif current_page == "Read a Book":
    st.markdown("### 📑 Read a Book")
    gutenberg_books = [b for b in st.session_state.personal_library if b.get("gutenberg_id")]

    if not gutenberg_books:
        st.markdown("""<div class='status-box'>
You have no free eBooks yet.<br>
Go to <b>Quick Search → Project Gutenberg</b> to find classics you can read here for free,
or ask the AI in Chat to find and add one for you!
</div>""", unsafe_allow_html=True)
    else:
        book_options = {b["id"]: f"{b['title']} — {b['author']}" for b in gutenberg_books}
        # Default to previously selected or first
        default_idx = 0
        if st.session_state.reading_book_id in book_options:
            default_idx = list(book_options.keys()).index(st.session_state.reading_book_id)
        selected_id = st.selectbox("Choose a book to read", options=list(book_options.keys()),
                                   format_func=lambda x: book_options[x], index=default_idx)

        if selected_id != st.session_state.reading_book_id:
            st.session_state.reading_book_id = selected_id
            st.session_state.reading_content = ""
            st.session_state.reading_offset = 0

        book = db_get_book(selected_id)
        if book:
            st.markdown(f"""
<div class='book-card' style='margin-bottom:16px'>
    <span class='book-title'>{book['title']}</span>
    <span class='book-author'> — {book['author']}</span>
    &nbsp;&nbsp;{render_stars(book.get('rating',0))}&nbsp;&nbsp;
    {status_badge(book.get('status','unread'))}
</div>""", unsafe_allow_html=True)

            if not st.session_state.reading_content:
                with st.spinner("Loading content from Project Gutenberg..."):
                    result = fetch_gutenberg_content(book["gutenberg_id"], 0)
                    if result["success"]:
                        st.session_state.reading_content = result["content"]
                        st.session_state.reading_offset = result["next_offset"]
                        if book.get("status") == "unread":
                            db_update_progress(book["id"], status="reading")
                            sync_library()
                    else:
                        st.error(f"Could not load: {result.get('error')}")

            if st.session_state.reading_content:
                st.markdown(f"<div class='reading-content'>{st.session_state.reading_content}</div>",
                            unsafe_allow_html=True)

                nav1, nav2, nav3 = st.columns(3)
                with nav1:
                    if st.button("⬅️ Previous section"):
                        new_off = max(0, st.session_state.reading_offset - 24000)
                        with st.spinner("Loading..."):
                            r = fetch_gutenberg_content(book["gutenberg_id"], new_off)
                            if r["success"]:
                                st.session_state.reading_content = r["content"]
                                st.session_state.reading_offset = new_off + 12000
                        st.rerun()
                with nav2:
                    if st.button("➡️ Next section"):
                        with st.spinner("Loading..."):
                            r = fetch_gutenberg_content(book["gutenberg_id"], st.session_state.reading_offset)
                            if r["success"]:
                                st.session_state.reading_content = r["content"]
                                st.session_state.reading_offset = r["next_offset"]
                            else:
                                st.info("You may have reached the end of the book!")
                        st.rerun()
                with nav3:
                    if st.button("🔄 Back to beginning"):
                        st.session_state.reading_content = ""
                        st.session_state.reading_offset = 0
                        st.rerun()

            st.markdown("---")
            st.markdown("**Update your progress:**")
            pc1, pc2, pc3, pc4 = st.columns(4)
            with pc1:
                npg = st.number_input("Current page", min_value=0, value=book.get("current_page",0) or 0, key="rpg")
            with pc2:
                ntpg = st.number_input("Total pages", min_value=0, value=book.get("total_pages",0) or 0, key="rtpg")
            with pc3:
                nst = st.selectbox("Status", ["unread","reading","finished"],
                                   index=["unread","reading","finished"].index(book.get("status","reading")),
                                   key="rst")
            with pc4:
                nrat = st.slider("Rating ★", 0, 5, value=book.get("rating",0) or 0, key="rrat")
            nrev = st.text_area("Review", value=book.get("review","") or "", key="rrev", height=60)
            if st.button("💾 Save Progress"):
                db_update_progress(book["id"], npg or None, ntpg or None, nst, nrat or None, nrev or None)
                sync_library(); st.success("Progress saved! ✅"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STATS
# ══════════════════════════════════════════════════════════════════════════════
elif current_page == "Stats":
    st.markdown("### 📊 Your Reading Stats")
    library = st.session_state.personal_library

    if not library:
        st.markdown("<div class='status-box'>Add some books to see your stats!</div>", unsafe_allow_html=True)
    else:
        total = len(library)
        reading = sum(1 for b in library if b.get("status") == "reading")
        finished = sum(1 for b in library if b.get("status") == "finished")
        unread = sum(1 for b in library if b.get("status") == "unread")
        ebooks = sum(1 for b in library if b.get("gutenberg_id"))
        rated = [b for b in library if b.get("rating")]
        avg_rating = round(sum(b["rating"] for b in rated) / len(rated), 1) if rated else 0

        cols = st.columns(5)
        for col, num, label in zip(cols, [total,reading,finished,unread,ebooks],
                                   ["Total Books","Reading Now","Finished","To Read","Free eBooks"]):
            with col:
                st.markdown(f"""
<div class='stat-card'>
    <div class='stat-number'>{num}</div>
    <div class='stat-label'>{label}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if rated:
            st.markdown(f"**Average Rating:** {render_stars(round(avg_rating))} "
                        f"({avg_rating}/5 across {len(rated)} rated books)", unsafe_allow_html=True)

        genres = {}
        for b in library:
            g = b.get("genre","Unknown") or "Unknown"
            genres[g] = genres.get(g, 0) + 1
        if genres:
            st.markdown("**Genre Breakdown:**")
            for g, cnt in sorted(genres.items(), key=lambda x: -x[1]):
                bar_w = int(cnt / total * 100)
                st.markdown(f"""
<div style='margin:5px 0'>
    <span style='color:var(--sienna);font-weight:600;display:inline-block;min-width:160px'>{g}</span>
    <span style='background:linear-gradient(90deg,var(--sienna),var(--gold));display:inline-block;
    height:14px;width:{bar_w}%;border-radius:4px;vertical-align:middle;margin:0 8px'></span>
    <span style='color:var(--muted)'>{cnt} book{'s' if cnt!=1 else ''}</span>
</div>""", unsafe_allow_html=True)

        finished_books = sorted(
            [b for b in library if b.get("status")=="finished" and b.get("finished_at")],
            key=lambda x: x.get("finished_at",""), reverse=True)
        if finished_books:
            st.markdown("**Recently Finished:**")
            for b in finished_books[:5]:
                st.markdown(f"""
<div style='padding:6px 0;border-bottom:1px solid var(--border)'>
    <b>{b['title']}</b> <span style='color:var(--muted)'>by {b['author']}</span>
    &nbsp;{render_stars(b.get('rating',0))}&nbsp;
    <span style='color:var(--muted);font-size:0.88rem'>Finished {b['finished_at']}</span>
</div>""", unsafe_allow_html=True)

        reading_now = [b for b in library if b.get("status")=="reading"]
        if reading_now:
            st.markdown("**Currently Reading:**")
            for b in reading_now:
                ph = render_progress_bar(b.get("current_page",0), b.get("total_pages",0))
                st.markdown(f"""
<div class='book-card'>
    <div class='book-title'>{b['title']}</div>
    <div class='book-author'>by {b['author']}</div>
    {ph}
    {"<div class='book-meta'>Started "+b['started_at']+"</div>" if b.get('started_at') else ""}
</div>""", unsafe_allow_html=True)
