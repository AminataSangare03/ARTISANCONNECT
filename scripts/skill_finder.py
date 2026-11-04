"""Utilitaire de recherche et d'indexation dynamique des competences de l'agent (Skills).

Permet de localiser instantanement n'importe quelle competence parmi les 500+ skills
disponibles en local sur la machine, meme si elle est marquee exclue du prompt systeme
en raison des limites de budget de contexte.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any


GLOBAL_SKILLS_DIR = os.path.expanduser(r'~/.gemini/config/skills')
PLUGINS_DIR = os.path.expanduser(r'~/.gemini/config/plugins')
WORKSPACE_SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.agents', 'skills'))
INDEX_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.agents', 'skills_index.json'))


def parse_skill_md(file_path: str) -> Dict[str, str]:
    """Extrait le nom et la description du frontmatter YAML d'un SKILL.md."""
    name = ''
    description = ''
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [f.readline() for _ in range(25)]
            in_frontmatter = False
            for line in lines:
                sline = line.strip()
                if sline == '---':
                    if in_frontmatter:
                        break
                    else:
                        in_frontmatter = True
                        continue
                if in_frontmatter:
                    if sline.startswith('name:'):
                        name = sline.replace('name:', '').strip().strip('\'"')
                    elif sline.startswith('description:'):
                        description = sline.replace('description:', '').strip().strip('\'"')
    except Exception:
        pass

    if not name:
        name = os.path.basename(os.path.dirname(file_path))

    return {'name': name, 'description': description, 'path': file_path}


def build_index() -> Dict[str, Any]:
    """Parcourt l'ensemble des repertoires pour indexer toutes les competences."""
    catalog: Dict[str, Any] = {}

    # 1. Competences de l'espace de travail (Priorite 1)
    if os.path.exists(WORKSPACE_SKILLS_DIR):
        for entry in sorted(os.listdir(WORKSPACE_SKILLS_DIR)):
            skill_md = os.path.join(WORKSPACE_SKILLS_DIR, entry, 'SKILL.md')
            if os.path.exists(skill_md):
                data = parse_skill_md(skill_md)
                data['scope'] = 'workspace'
                data['priority'] = 1
                catalog[data['name']] = data

    # 2. Competences globales
    if os.path.exists(GLOBAL_SKILLS_DIR):
        for entry in sorted(os.listdir(GLOBAL_SKILLS_DIR)):
            skill_md = os.path.join(GLOBAL_SKILLS_DIR, entry, 'SKILL.md')
            if os.path.exists(skill_md) and entry not in catalog:
                data = parse_skill_md(skill_md)
                data['scope'] = 'global'
                data['priority'] = 2
                catalog[data['name']] = data

    # 3. Competences issues des plugins
    if os.path.exists(PLUGINS_DIR):
        for root, _, files in os.walk(PLUGINS_DIR):
            if 'SKILL.md' in files:
                skill_md = os.path.join(root, 'SKILL.md')
                data = parse_skill_md(skill_md)
                if data['name'] not in catalog:
                    data['scope'] = 'plugin'
                    data['priority'] = 3
                    catalog[data['name']] = data

    # Sauvegarde de l'index au format JSON
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    return catalog


def load_index(force_refresh: bool = False) -> Dict[str, Any]:
    """Charge l'index depuis le cache disque ou le reconstruit."""
    if not force_refresh and os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return build_index()


def search_skills(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """Recherche des competences par mots-cles."""
    catalog = load_index()
    q_tokens = query.lower().split()

    scored = []
    for name, item in catalog.items():
        score = 0
        name_lower = name.lower()
        desc_lower = (item.get('description') or '').lower()

        # Score prioritaire sur le scope de travail
        if item.get('scope') == 'workspace':
            score += 5

        # Correspondance exacte du nom
        if query.lower() == name_lower:
            score += 100

        for token in q_tokens:
            if token in name_lower:
                score += 30
            if token in desc_lower:
                score += 10

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]


def main():
    parser = argparse.ArgumentParser(description="Recherche de competences pour l'agent Antigravity.")
    parser.add_argument('query', nargs='?', default='', help='Mot-cle de recherche (ex: docker, security, ui)')
    parser.add_argument('--index', action='store_true', help='Reconstruire le fichier d indexation JSON')
    parser.add_argument('--count', action='store_true', help='Afficher le nombre total de competences indexees')
    parser.add_argument('--workspace', action='store_true', help='Lister uniquement les competences de lespace de travail')
    args = parser.parse_args()

    if args.index:
        catalog = build_index()
        print(f"[INDEXATION TERMINEE] {len(catalog)} competences indexees dans {INDEX_FILE}")
        return

    catalog = load_index()

    if args.count:
        w_count = sum(1 for v in catalog.values() if v.get('scope') == 'workspace')
        g_count = sum(1 for v in catalog.values() if v.get('scope') == 'global')
        p_count = sum(1 for v in catalog.values() if v.get('scope') == 'plugin')
        print(f"Total des competences disponibles : {len(catalog)}")
        print(f" - Workspace (.agents/skills)   : {w_count}")
        print(f" - Global (~/.gemini/config)    : {g_count}")
        print(f" - Plugins (~/.gemini/plugins)  : {p_count}")
        return

    if args.workspace:
        print("[COMPETENCES PRIORITAIRES WORKSPACE (Priorite 1)]")
        for k, v in sorted(catalog.items()):
            if v.get('scope') == 'workspace':
                print(f"- {k} : {v.get('description', '')[:90]}...")
        return

    if not args.query:
        print("Usage: python scripts/skill_finder.py <terme_de_recherche> | --count | --index | --workspace")
        return

    results = search_skills(args.query)
    if not results:
        print(f"Aucune competence correspondant a '{args.query}'.")
        return

    print(f"Resultats pour '{args.query}' ({len(results)} trouves) :")
    for r in results:
        scope_tag = f"[{r.get('scope').upper()}]"
        print(f"\n{scope_tag} {r['name']}")
        print(f"Chemin: file:///{r['path'].replace(os.sep, '/')}")
        if r.get('description'):
            print(f"Role: {r['description']}")


if __name__ == '__main__':
    main()
