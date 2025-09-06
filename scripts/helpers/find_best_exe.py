import os
import difflib
from utils import get_all_drives, token_overlap_score, normalize_text
import re

# def find_best_exe(target_name, max_depth=6):
#     """
#     Recursively searches for the best-matching .exe file in all drives using multiple similarity strategies.
#     Args:
#         target_name (str): The target executable name to search for.
#         max_depth (int, optional): Maximum directory depth to search. Defaults to 6.

#     Returns:
#         str or None: Path to the best-matching .exe file, or None if not found.
#     """
#     search_dirs = get_all_drives()
#     target_name_norm = target_name.lower().replace('.exe', '').replace(' ', '')
#     seen = set()
#     scored_paths = []
#     scored_paths_token = []
#     scored_paths_boost = []
#     scored_paths_min = []
#     boost_scores = {}

#     def score(candidate_path):
#         base = os.path.basename(candidate_path).lower().replace(
#             '.exe', '').replace(' ', '')
#         folder = os.path.dirname(candidate_path).lower().replace(' ', '')
#         name_score = difflib.SequenceMatcher(
#             None, target_name_norm, base).ratio()
#         folder_score = difflib.SequenceMatcher(
#             None, target_name_norm, folder).ratio()
#         weighted = name_score * 0.7 + folder_score * 0.3
#         return weighted, name_score, folder_score, base, folder

#     def walk_dir(root, depth):
#         if depth > max_depth:
#             return
#         try:
#             for entry in os.scandir(root):
#                 if entry.is_dir(follow_symlinks=False):
#                     walk_dir(entry.path, depth + 1)
#                 elif entry.is_file() and entry.name.lower().endswith('.exe'):
#                     full_path = entry.path
#                     if full_path in seen:
#                         continue
#                     seen.add(full_path)
#                     weighted, name_score, folder_score, base, folder = score(
#                         full_path)
#                     scored_paths.append(
#                         (weighted, full_path, {'name_score': name_score, 'folder_score': folder_score}))
#                     token_score = token_overlap_score(
#                         target_name_norm, base + ' ' + folder)
#                     scored_paths_token.append((token_score, full_path, {}))
#                     boost = weighted
#                     if target_name_norm in folder:
#                         print(
#                             f"Boosting {base} because it contains {target_name_norm}")
#                         boost += 0.2

#                     scored_paths_boost.append((boost, full_path, {}))
#                     boost_scores[full_path] = boost
#                     if name_score > 0.2 and folder_score > 0.2:
#                         scored_paths_min.append((weighted, full_path, {}))
#         except Exception:
#             pass  # Ignore permission errors, etc.

#     for d in search_dirs:
#         if d and os.path.exists(d):
#             walk_dir(d, 0)

#     def print_top(title, arr):
#         arr = sorted(arr, reverse=True, key=lambda x: x[0])
#         print(f"\nTop 5 .exe matches ({title}):")
#         for i, (s, p, *_) in enumerate(arr[:5]):
#             print(f"{i+1}. Score: {s:.3f} | Path: {p}")
#         return [p for _, p, *_ in arr[:5]]

#     top_boosted = print_top('boosted', scored_paths_boost)
#     top_token = print_top('token overlap', scored_paths_token)
#     top_min = print_top('min name/folder > 0.2', scored_paths_min)

#     all_top = top_boosted + top_token + top_min
#     counter = Counter(all_top)
#     if not counter:
#         return None
#     most_common = counter.most_common()
#     max_count = most_common[0][1]
#     candidates = [exe for exe, count in most_common if count == max_count]
#     if len(candidates) > 1:
#         candidates.sort(key=lambda p: boost_scores.get(p, 0), reverse=True)
#     consensus_exe = candidates[0]
#     print(
#         f"\nConsensus result: {consensus_exe} (appeared {max_count} times in top 5s)")
#     return consensus_exe


def path_penalty_boost(path, target_tokens):
    """
    Calculates a penalty or boost for a given executable path based on its context.
    Uses generic heuristics rather than hardcoded specific names.

    Args:
        path (str): The full path to the executable file.
        target_tokens (list of str): List of normalized tokens from the target name.
        target_name_norm (str): The normalized target name.

    Returns:
        float: The penalty/boost score to be added to the final score.
    """
    path_lower = path.lower()
    penalty = 0
    boost = 0

    system_keywords = [
        r"windows\\system32", r"windows\\syswow64", r"windows\\winsxs",
        r"\\installer\\", r"\\redistributables\\", r"\\support\\"
    ]
    for kw in system_keywords:
        if re.search(kw, path_lower):
            penalty -= 0.1

    folder_name = os.path.basename(os.path.dirname(path)).lower()
    parent_folder = os.path.basename(
        os.path.dirname(os.path.dirname(path))).lower()

    target_in_folder = any(
        token in folder_name for token in target_tokens if len(token) > 2)
    target_in_parent = any(
        token in parent_folder for token in target_tokens if len(token) > 2)

    if target_in_folder:
        boost += 0.15
    if target_in_parent:
        boost += 0.1

    generic_folders = ["bin", "exe", "executables",
                       "apps", "applications", "tools", "utilities"]
    if folder_name in generic_folders:
        penalty -= 0.05

    if all(token in path_lower for token in target_tokens if len(token) > 2):
        boost += 0.2

    if any(x in path_lower for x in ["redistributable", "installer", "setup", "support", "helper"]):
        penalty -= 0.15

    if re.search(r'\\\d+\.\d+\.\d+', path_lower):
        penalty -= 0.05

    if "program files" in path_lower:
        if not any(sys_kw in path_lower for sys_kw in ["windows", "microsoft", "system32"]):
            if target_in_folder or target_in_parent:
                boost += 0.05

    return penalty + boost


def find_best_exe(target_name, max_depth=6, verbose=True, return_all=False):
    """
    Searches for the best-matching .exe file in all drives using advanced similarity and context strategies.

    Args:
        target_name (str): The target executable name to search for.
        max_depth (int, optional): Maximum directory depth to search. Defaults to 6.
        verbose (bool, optional): If True, prints detailed scoring info. Defaults to True.
        return_all (bool, optional): If True, returns a ranked list of candidates. Defaults to False.

    Returns:
        str or list: Path to the best-matching .exe file, or ranked list if return_all is True.
    """
    search_dirs = get_all_drives()
    target_name_norm = normalize_text(target_name.replace('.exe', ''))
    target_tokens = [t for t in re.split(r'\W+', target_name_norm) if t]
    seen = set()
    scored_paths = []

    def score(candidate_path):
        """
        Calculates a similarity score for a candidate executable path.

        Args:
            candidate_path (str): The full path to the candidate executable.

        Returns:
            tuple: (score (float), details (dict))
        """
        base = os.path.basename(candidate_path)
        folder = os.path.dirname(candidate_path)
        base_norm = normalize_text(base.replace('.exe', ''))
        folder_norm = normalize_text(folder)
        seq_score = difflib.SequenceMatcher(
            None, target_name_norm, base_norm).ratio()
        token_score = token_overlap_score(
            target_name_norm, base_norm + ' ' + folder_norm)
        all_tokens_in_base = all(
            token in base_norm for token in target_tokens if len(token) > 2)
        all_tokens_in_path = all(token in (base_norm + ' ' + folder_norm)
                                 for token in target_tokens if len(token) > 2)
        path_boost = path_penalty_boost(candidate_path, target_tokens)
        exact = int(target_name_norm == base_norm)
        substr = int(
            target_name_norm in base_norm or base_norm in target_name_norm)
        score = (
            seq_score * 0.4 +
            token_score * 0.25 +
            exact * 0.25 +
            substr * 0.05 +
            all_tokens_in_base * 0.15 +
            all_tokens_in_path * 0.1 +
            path_boost
        )
        return score, {
            'seq_score': seq_score,
            'token_score': token_score,
            'exact': exact,
            'substr': substr,
            'all_tokens_in_base': all_tokens_in_base,
            'all_tokens_in_path': all_tokens_in_path,
            'path_boost': path_boost,
            'base': base,
            'folder': folder
        }

    def walk_dir(root, depth):
        """
        Recursively walks through directories to find .exe files up to a maximum depth.

        Args:
            root (str): The root directory to start searching from.
            depth (int): The current depth in the directory tree.
        """
        if depth > max_depth:
            return
        try:
            for entry in os.scandir(root):
                if entry.is_dir(follow_symlinks=False):
                    walk_dir(entry.path, depth + 1)
                elif entry.is_file() and entry.name.lower().endswith('.exe'):
                    full_path = entry.path
                    if full_path in seen:
                        continue
                    seen.add(full_path)
                    s, details = score(full_path)
                    scored_paths.append((s, full_path, details))
        except Exception:
            pass

    for d in search_dirs:
        if d and os.path.exists(d):
            walk_dir(d, 0)

    scored_paths.sort(reverse=True, key=lambda x: x[0])
    if verbose:
        print(f"\nTop 7 .exe matches (improved):")
        for i, (s, p, details) in enumerate(scored_paths[:7]):
            print(f"{i+1}. Score: {s:.3f} | Path: {p} | Details: {details}")
    if not scored_paths:
        return None if not return_all else []
    if return_all:
        return scored_paths
    return scored_paths[0][1]
