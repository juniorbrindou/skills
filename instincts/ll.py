#!/usr/bin/env python3
"""Apprentissage continu local : synthèse des observations, instincts, promotion.

Sous-commandes :
  digest [--all] [--project ID]   candidats tirés des observations (corrections, gestes répétés, erreurs répétées)
  status                          instincts, confiance après décroissance
  add ID --trigger T --action A [--domain D] [--scope project|global] [--project ID] [--evidence E]
                                  crée l'instinct (confiance 0.3) ou le renforce (+0.1)
  weaken ID [--project ID]        correction explicite : -0.2
  promote [ID] [--apply]          instincts présents dans 2 projets ou plus avec confiance moyenne >= 0.8 -> global

Règles de confiance : 0.3 à la création, +0.1 par renforcement (max 0.9), -0.2 si contredit,
-0.1 par tranche de 30 jours sans preuve (plancher 0.1), calculé à la lecture.
"""
import argparse
import collections
import datetime
import json
import os
import re
import sys
import time

BASE = os.environ.get("LOCAL_LEARNING_DIR") or os.path.join(
    os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"), "local-learning"
)
NEW, STEP, MAX, MIN, WEAKEN = 0.3, 0.1, 0.9, 0.1, 0.2
DECAY_DAYS, DECAY_STEP = 30, 0.1
PROMOTE_MIN_PROJECTS, PROMOTE_MIN_CONF = 2, 0.8
CORRECTION = re.compile(
    r"(?i)\b(non\b|pas ça|pas comme|arrête|arrete|stop\b|trop (?:long|verbeux|de)|plus court|ne fais pas|ne touche pas|"
    r"jamais|toujours|je t'ai dit|je t’ai dit|encore\b|laisse tomber|ce n'est pas|c'est pas)"
)


def projects():
    d = os.path.join(BASE, "projects")
    return sorted(os.listdir(d)) if os.path.isdir(d) else []


def meta(pid):
    try:
        return json.load(open(os.path.join(BASE, "projects", pid, "project.json")))
    except Exception:
        return {"id": pid, "name": pid, "key": ""}


def observations(pid):
    p = os.path.join(BASE, "projects", pid, "observations.jsonl")
    out = []
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def state_path(pid):
    return os.path.join(BASE, "projects", pid, "digest-state.json")


def norm_command(cmd):
    """Un geste = les trois premiers mots (sans sudo ni cd), sans chiffres ni empreintes."""
    cmd = re.sub(r"^\s*(?:cd\s+\S+\s*&&\s*)+", "", cmd)
    mots = re.sub(r"\b[0-9a-f]{7,}\b|\d+", "N", cmd).split()
    if mots and mots[0] == "sudo":
        mots = mots[1:]
    return " ".join(mots[:3]) if mots else ""


def digest(args):
    cibles = [args.project] if args.project else projects()
    resultat = []
    for pid in cibles:
        obs = observations(pid)
        depuis = 0 if args.all else (json.load(open(state_path(pid))).get("last_t", 0) if os.path.exists(state_path(pid)) else 0)
        nouvelles = [o for o in obs if o.get("t", 0) > depuis]
        if not nouvelles:
            continue
        corrections = [
            {"t": o["t"], "text": o["text"]}
            for o in nouvelles
            if o.get("kind") == "prompt" and CORRECTION.search(o.get("text", ""))
        ]
        gestes = collections.defaultdict(lambda: {"n": 0, "sessions": set(), "exemple": ""})
        for o in nouvelles:
            if o.get("kind") == "tool" and o.get("tool") == "Bash":
                g = norm_command(o.get("call", ""))
                if g:
                    gestes[g]["n"] += 1
                    gestes[g]["sessions"].add(o.get("session"))
                    gestes[g]["exemple"] = o["call"][:140]
        repetes = sorted(
            ({"geste": g, "fois": v["n"], "sessions": len(v["sessions"]), "exemple": v["exemple"]} for g, v in gestes.items() if v["n"] >= 3),
            key=lambda x: -x["fois"],
        )[:10]
        erreurs = collections.Counter(
            (o.get("tool"), o.get("error", "")[:70]) for o in nouvelles if o.get("kind") == "tool" and not o.get("ok", True)
        )
        erreurs_rep = [{"outil": t, "message": m, "fois": n} for (t, m), n in erreurs.most_common(5) if n >= 2]
        m = meta(pid)
        resultat.append(
            {
                "project_id": pid,
                "project": m.get("name"),
                "observations": len(nouvelles),
                "corrections": corrections[-15:],
                "gestes_repetes": repetes,
                "erreurs_repetees": erreurs_rep,
            }
        )
        if not args.peek:
            json.dump({"last_t": max(o["t"] for o in nouvelles)}, open(state_path(pid), "w"))
    print(json.dumps(resultat, ensure_ascii=False, indent=1))


def idir(scope, pid):
    return os.path.join(BASE, "projects", pid, "instincts") if scope == "project" else os.path.join(BASE, "instincts", "personal")


def lire(path):
    texte = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n(.*)", texte, re.S)
    entete = {}
    for ligne in m.group(1).split("\n"):
        k, _, v = ligne.partition(": ")
        entete[k] = v
    return entete, m.group(2)


def ecrire(path, entete, corps):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("---\n" + "\n".join(f"{k}: {v}" for k, v in entete.items()) + "\n---\n" + corps)


def confiance(entete, maintenant=None):
    maintenant = maintenant or time.time()
    c = float(entete.get("confidence", NEW))
    jours = (maintenant - int(entete.get("last_seen", maintenant))) / 86400
    c -= DECAY_STEP * int(jours // DECAY_DAYS)
    return round(max(MIN, c), 2)


def tous():
    out = []
    g = idir("global", "")
    if os.path.isdir(g):
        out += [(f, "global", None, os.path.join(g, f)) for f in sorted(os.listdir(g)) if f.endswith(".md")]
    for pid in projects():
        d = idir("project", pid)
        if os.path.isdir(d):
            out += [(f, "project", pid, os.path.join(d, f)) for f in sorted(os.listdir(d)) if f.endswith(".md")]
    return out


def add(args):
    scope = args.scope
    pid = args.project or ""
    if scope == "project" and not pid:
        sys.exit("--project est requis pour un instinct de projet (voir `digest`).")
    path = os.path.join(idir(scope, pid), f"{args.id}.md")
    now = int(time.time())
    if os.path.exists(path):
        entete, corps = lire(path)
        entete["confidence"] = round(min(MAX, confiance(entete) + STEP), 2)
        entete["last_seen"] = now
        entete["evidence_count"] = int(entete.get("evidence_count", 1)) + 1
        corps += f"- {datetime.date.today()} : {args.evidence or 'renforcé'}\n"
        action = "renforcé"
    else:
        entete = {
            "id": args.id, "trigger": args.trigger, "confidence": NEW, "domain": args.domain or "general", "scope": scope,
            "project_id": pid, "project_name": meta(pid).get("name", "") if pid else "", "created": now, "last_seen": now,
            "evidence_count": 1,
        }
        corps = f"\n## Action\n{args.action}\n\n## Evidence\n- {datetime.date.today()} : {args.evidence or 'première observation'}\n"
        action = "créé"
    ecrire(path, entete, corps)
    print(f"{action} : {args.id} ({scope}) confiance {entete['confidence']}")


def weaken(args):
    for f, scope, pid, path in tous():
        if f == f"{args.id}.md" and (not args.project or pid == args.project):
            entete, corps = lire(path)
            entete["confidence"] = round(max(MIN, confiance(entete) - WEAKEN), 2)
            entete["last_seen"] = int(time.time())
            corps += f"- {datetime.date.today()} : contredit par l'utilisateur\n"
            ecrire(path, entete, corps)
            print(f"affaibli : {args.id} -> {entete['confidence']}")
            return
    sys.exit("instinct introuvable")


def status(_):
    lignes = []
    for f, scope, pid, path in tous():
        e, _c = lire(path)
        lignes.append((confiance(e), e["id"], scope, e.get("project_name") or "-", e.get("domain"), e.get("trigger")))
    if not lignes:
        print("Aucun instinct.")
    for c, i, s, p, d, t in sorted(lignes, reverse=True):
        print(f"{c:.1f}  {i}  [{s}:{p}] ({d})  {t}")


def promote(args):
    par_id = collections.defaultdict(list)
    for f, scope, pid, path in tous():
        if scope == "project":
            e, _c = lire(path)
            par_id[e["id"]].append((pid, path, e))
    propositions = []
    for i, items in par_id.items():
        if args.id and i != args.id:
            continue
        moyenne = sum(confiance(e) for _p, _x, e in items) / len(items)
        if len({p for p, _x, _e in items}) >= PROMOTE_MIN_PROJECTS and moyenne >= PROMOTE_MIN_CONF:
            propositions.append((i, items, round(moyenne, 2)))
    if not propositions:
        print(f"Rien à promouvoir (il faut {PROMOTE_MIN_PROJECTS} projets et une confiance moyenne >= {PROMOTE_MIN_CONF}).")
        return
    for i, items, moyenne in propositions:
        print(f"{'PROMOUVOIR' if args.apply else 'à promouvoir'} : {i} (projets : {', '.join(e.get('project_name', '?') for _p, _x, e in items)}, confiance moyenne {moyenne})")
        if args.apply:
            _p, _x, e = items[0]
            corps = open(items[0][1], encoding="utf-8").read().split("---\n", 2)[2]
            e = dict(e, scope="global", project_id="", project_name="", confidence=moyenne, last_seen=int(time.time()))
            ecrire(os.path.join(idir("global", ""), f"{i}.md"), e, corps)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    d = s.add_parser("digest"); d.add_argument("--all", action="store_true"); d.add_argument("--project"); d.add_argument("--peek", action="store_true"); d.set_defaults(f=digest)
    a = s.add_parser("add"); a.add_argument("id"); a.add_argument("--trigger", required=True); a.add_argument("--action", required=True)
    a.add_argument("--domain"); a.add_argument("--scope", choices=["project", "global"], default="project"); a.add_argument("--project"); a.add_argument("--evidence"); a.set_defaults(f=add)
    w = s.add_parser("weaken"); w.add_argument("id"); w.add_argument("--project"); w.set_defaults(f=weaken)
    st = s.add_parser("status"); st.set_defaults(f=status)
    pr = s.add_parser("promote"); pr.add_argument("id", nargs="?"); pr.add_argument("--apply", action="store_true"); pr.set_defaults(f=promote)
    args = p.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
