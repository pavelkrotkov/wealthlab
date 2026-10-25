"""Synthetic Git metadata entirely inside the selected test runtime directory."""


def linked_checkouts(tmp_path):
    main, current, sibling = (tmp_path / name for name in ("public", "current", "sibling"))
    common = main / ".git"
    for name, root in (("current", current), ("sibling", sibling)):
        root.mkdir(parents=True)
        metadata = common / "worktrees" / name
        metadata.mkdir(parents=True)
        (metadata / "commondir").write_text("../..", encoding="utf-8")
        (metadata / "gitdir").write_text(str(root / ".git"), encoding="utf-8")
        (root / ".git").write_text(f"gitdir: {metadata}", encoding="utf-8")
    return main, current, sibling
