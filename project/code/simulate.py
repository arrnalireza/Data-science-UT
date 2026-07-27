import os
import numpy as np
import pandas as pd


class TournamentSimulator:
    def __init__(self, model_ensemble, weights, host_teams=None, max_rest_day=14):
        self.models= model_ensemble
        self.weights= weights
        self.host_teams= host_teams or ["Mexico", "USA", "Canada"]
        self.max_rest_day= max_rest_day
        self.group_match_dates= {
            "A": [pd.Timestamp(d) for d in ["2026-06-11", "2026-06-18", "2026-06-24"]],
            "B": [pd.Timestamp(d) for d in ["2026-06-12", "2026-06-18", "2026-06-24"]],
            "C": [pd.Timestamp(d) for d in ["2026-06-13", "2026-06-19", "2026-06-24"]],
            "D": [pd.Timestamp(d) for d in ["2026-06-13", "2026-06-19", "2026-06-25"]],
            "E": [pd.Timestamp(d) for d in ["2026-06-14", "2026-06-20", "2026-06-25"]],
            "F": [pd.Timestamp(d) for d in ["2026-06-14", "2026-06-20", "2026-06-25"]],
            "G": [pd.Timestamp(d) for d in ["2026-06-15", "2026-06-21", "2026-06-26"]],
            "H": [pd.Timestamp(d) for d in ["2026-06-15", "2026-06-21", "2026-06-26"]],
            "I": [pd.Timestamp(d) for d in ["2026-06-16", "2026-06-22", "2026-06-26"]],
            "J": [pd.Timestamp(d) for d in ["2026-06-16", "2026-06-22", "2026-06-27"]],
            "K": [pd.Timestamp(d) for d in ["2026-06-17", "2026-06-23", "2026-06-27"]],
            "L": [pd.Timestamp(d) for d in ["2026-06-17", "2026-06-23", "2026-06-27"]],
        }

        self.r32_matches= [
            (("R", "A"), ("R", "B")),
            (("W", "E"), ("T", "ABCDF")),
            (("W", "F"), ("R", "C")),
            (("W", "C"), ("R", "F")),
            (("W", "I"), ("T", "CDFGH")),
            (("R", "E"), ("R", "I")),
            (("W", "A"), ("T", "CEFHI")),
            (("W", "L"), ("T", "EHIJK")),
            (("W", "D"), ("T", "BEFIJ")),
            (("W", "G"), ("T", "AEHIJ")),
            (("R", "K"), ("R", "L")),
            (("W", "H"), ("R", "J")),
            (("W", "B"), ("T", "EFGIJ")),
            (("W", "J"), ("R", "H")),
            (("W", "K"), ("T", "DEIJL")),
            (("R", "D"), ("R", "G")),
        ]

        self.r16_pairs= [(1, 4), (0, 2), (3, 5), (6, 7), (11, 10), (8, 9), (13, 15), (12, 14)]
        self.qf_pairs= [(0, 1), (4, 5), (2, 3), (6, 7)]
        self.sf_pairs= [(0, 1), (2, 3)]

        self.r32_dates= [
            pd.Timestamp(d)
            for d in [
                "2026-06-28", "2026-06-29", "2026-06-29", "2026-06-29",
                "2026-06-30", "2026-06-30", "2026-06-30", "2026-07-01",
                "2026-07-01", "2026-07-01", "2026-07-02", "2026-07-02",
                "2026-07-02", "2026-07-03", "2026-07-03", "2026-07-03",
            ]
        ]
        self.r16_dates= [
            pd.Timestamp(d)
            for d in [
                "2026-07-04", "2026-07-04", "2026-07-05", "2026-07-05",
                "2026-07-06", "2026-07-06", "2026-07-07", "2026-07-07",
            ]
        ]
        self.qf_dates= [
            pd.Timestamp(d)
            for d in ["2026-07-09", "2026-07-10", "2026-07-11", "2026-07-11"]
        ]
        self.sf_dates = [pd.Timestamp(d) for d in ["2026-07-14", "2026-07-15"]]
        self.final_date = pd.Timestamp("2026-07-19")

    def _is_neutral(self, home, away):
        neutral= True
        if home in self.host_teams:
            neutral = False
        elif away in self.host_teams:
            home, away = away, home
            neutral = False
        return home, away, neutral

    def _compute_h2h_features(self, home, away, h2h_history):
        matches= h2h_history[home][away]
        total= len(matches)
        is_first= 1 if total == 0 else 0

        if is_first:
            return {
                "h2h_last5_home_winrate": 0.5,
                "h2h_last5_avg_gd": 0,
                "h2h_total_matches": 0,
                "h2h_is_first_meeting": 1,
            }
        last5= matches[-5:]
        gd_sum= sum(last5)
        wins= sum(1 for gd in last5 if gd > 0)

        return {
            "h2h_last5_home_winrate": wins / len(last5),
            "h2h_last5_avg_gd": gd_sum / len(last5),
            "h2h_total_matches": total,
            "h2h_is_first_meeting": is_first,
        }

    def _compute_rest_features(self, hf, af, current_date):
        home_rest= min((current_date - hf["last_match_date"]).days, self.max_rest_day)
        away_rest= min((current_date - af["last_match_date"]).days, self.max_rest_day)
        return {
            "home_rest": home_rest,
            "away_rest": away_rest,
            "rest_diff": home_rest - away_rest,
        }

    def _predict_gd(self, configs, team_features, h2h_history):
        rows= []
        for d in configs.values():
            home, away = d["home_team"], d["away_team"]
            neutral, date = d["neutral"], d["date"]
            hf= team_features[home]
            af= team_features[away]
            elo_home_eff = hf["elo"] + (0 if neutral else 100)
            e_home= 1/(1 + 10**((af["elo"] - elo_home_eff)/400))
            h2h_feats = self._compute_h2h_features(home, away, h2h_history)
            rest_feats = self._compute_rest_features(hf, af, date)
            team_features[home]["last_match_date"] = date
            team_features[away]["last_match_date"] = date

            row= {
                "neutral": neutral,
                "home_rank": hf["rank"],
                "home_fifa_points": hf["fifa_points"],
                "away_rank": af["rank"],
                "away_fifa_points": af["fifa_points"],
                "home_avg_age": hf["avg_age"],
                "home_avg_value": hf["avg_value"],
                "away_avg_age": af["avg_age"],
                "away_avg_value": af["avg_value"],
                "home_rank_tier": hf["rank_tier"],
                "away_rank_tier": af["rank_tier"],
                "rank_diff": af["rank"] - hf["rank"],
                "home_last5_winrate": hf["last5_winrate"],
                "home_last5_avg_sd": hf["last5_avg_sd"],
                "away_last5_winrate": af["last5_winrate"],
                "away_last5_avg_sd": af["last5_avg_sd"],
                "match_type_ordinal": 3,
                "is_friendly": 0,
                "elo_home_pre": hf["elo"],
                "elo_away_pre": af["elo"],
                "elo_diff": hf["elo"] - af["elo"],
                "elo_win_prob": e_home,
                "fifa_points_diff": hf["fifa_points"] - af["fifa_points"],
                "rank_ratio": af["rank"] / hf["rank"],
                "tier_diff": af["rank_tier"] - hf["rank_tier"],
                "winrate_diff": hf["last5_winrate"] - af["last5_winrate"],
                "avg_sd_diff": hf["last5_avg_sd"] - af["last5_avg_sd"],
                "value_diff": hf["avg_value"] - af["avg_value"],
                "value_ratio": hf["avg_value"] / af["avg_value"],
                "age_diff": hf["avg_age"] - af["avg_age"],
                "h2h_last5_home_winrate": h2h_feats["h2h_last5_home_winrate"],
                "h2h_last5_avg_gd": h2h_feats["h2h_last5_avg_gd"],
                "h2h_total_matches": h2h_feats["h2h_total_matches"],
                "h2h_is_first_meeting": h2h_feats["h2h_is_first_meeting"],
                "home_days_rest": rest_feats["home_rest"],
                "away_days_rest": rest_feats["away_rest"],
                "rest_diff": rest_feats["rest_diff"],
            }
            rows.append(row)

        X= pd.DataFrame(rows)
        X = X.apply(pd.to_numeric, errors="coerce").fillna(0)

        xgb_m, lgb_m, cat_m = self.models
        w = self.weights

        xgb_pred = xgb_m.predict(X)
        lgb_pred = lgb_m.predict(X)
        cat_pred = cat_m.predict(X)
        return w[0] * xgb_pred + w[1] * lgb_pred + w[2] * cat_pred

    def _group_config_maker(self, groups):
        configs= {}
        match_idx= 0
        matchdays= [[(0, 1), (2, 3)], [(0, 2), (3, 1)], [(3, 0), (1, 2)]]
        for group_letter, group_teams in groups.items():
            dates= self.group_match_dates[group_letter]
            for idx, pairings in enumerate(matchdays):
                current_date = dates[idx]
                for i, j in pairings:
                    home, away = group_teams[i], group_teams[j]
                    home, away, neutral = self._is_neutral(home, away)
                    configs[match_idx] = {
                        "home_team": home,
                        "away_team": away,
                        "date": current_date,
                        "neutral": neutral,
                        "group_letter": group_letter,
                    }
                    match_idx += 1
        return configs

    def _simulate_group(self, groups, team_features, h2h_history):
        stats= {l: {t: {"pts": 0, "gd": 0} for t in groups[l]} for l in groups}
        h2h= {l: {t1: {t2: 0 for t2 in groups[l]} for t1 in groups[l]} for l in groups}
        configs= self._group_config_maker(groups)

        diff= self._predict_gd(configs, team_features, h2h_history)
        diff += np.random.normal(0, 0.8, size=len(diff))
        diff_round = np.round(diff).astype(int)

        for i in range(len(diff_round)):
            c= configs[i]
            home, away, group= c["home_team"], c["away_team"], c["group_letter"]

            if diff_round[i] > 0:
                stats[group][home]["pts"] += 3
                h2h[group][home][away], h2h[group][away][home] = 3, 0
            elif diff_round[i] == 0:
                stats[group][home]["pts"] += 1
                stats[group][away]["pts"] += 1
                h2h[group][home][away], h2h[group][away][home] = 1, 1
            else:
                stats[group][away]["pts"] += 3
                h2h[group][away][home], h2h[group][home][away] = 3, 0

            stats[group][home]["gd"] += diff_round[i]
            stats[group][away]["gd"] -= diff_round[i]

        standings= []
        for group in groups:
            all_teams = list(groups[group])
            all_teams.sort(key=lambda t: (-stats[group][t]["pts"], -stats[group][t]["gd"], team_features[t]["rank"]))
            for i in range(len(all_teams) - 1):
                t1, t2 = all_teams[i], all_teams[i + 1]
                if (stats[group][t1]["pts"] == stats[group][t2]["pts"] and stats[group][t1]["gd"] == stats[group][t2]["gd"]):
                    if h2h[group][t2][t1] > h2h[group][t1][t2]:
                        all_teams[i], all_teams[i + 1] = all_teams[i + 1], all_teams[i]

            standings.append({
                "group": group,
                "table": [{"team": t, "pts": stats[group][t]["pts"], "gd": stats[group][t]["gd"], "rank": team_features[t]["rank"]} for t in all_teams]
            })
        return standings

    def _map_third_place_teams(self, best_thirds):
        t_slots= []
        for home, away in self.r32_matches:
            if home[0] == "T": t_slots.append(home[1])
            if away[0] == "T": t_slots.append(away[1])

        def solve(slot_idx, used_indices):
            if slot_idx == len(t_slots): return []
            current_constraint = t_slots[slot_idx]
            for i, t in enumerate(best_thirds):
                if i not in used_indices and t["group"] in current_constraint:
                    res = solve(slot_idx + 1, used_indices | {i})
                    if res is not None:
                        return [t["team"]] + res
            return None
        ordered_teams = solve(0, set())
        return {t_slots[i]: ordered_teams[i] for i in range(len(t_slots))}

    def _simulate_knockout_round(self, matches, dates, team_features, h2h_history):
        winners= []
        configs= {
            idx: {"home_team": h, "away_team": a, "date": d, "neutral": self._is_neutral(h, a)[2]}
            for idx, ((h, a), d) in enumerate(zip(matches, dates))
        }

        diff= self._predict_gd(configs, team_features, h2h_history)
        diff+= np.random.normal(0, 1.2, size=len(diff))
        diff_round = np.round(diff).astype(int)

        for i in range(len(diff_round)):
            c= configs[i]
            home, away= c["home_team"], c["away_team"]
            if diff_round[i] > 0:
                winners.append(home)
            elif diff_round[i] < 0:
                winners.append(away)
            else:
                winners.append(home if np.random.random() < 0.5 else away)
        return winners

    def simulate_single_tournament(self, groups, team_features, h2h_history):
        standings= self._simulate_group(groups, team_features, h2h_history)
        winners, runners_up, thirds= {}, {}, []
        for g_data in standings:
            g= g_data["group"]
            tbl= g_data["table"]
            winners[g], runners_up[g] = tbl[0]["team"], tbl[1]["team"]
            thirds.append({**tbl[2], "group": g})

        best_thirds = sorted(thirds, key=lambda x: (-x["pts"], -x["gd"], x["rank"]))[:8]
        t_mapping = self._map_third_place_teams(best_thirds)
        advanced = list(winners.values()) + list(runners_up.values()) + list(t_mapping.values())

        r32_matches= []
        for home_slot, away_slot in self.r32_matches:
            h_team= winners[home_slot[1]] if home_slot[0] == "W" else (runners_up[home_slot[1]] if home_slot[0] == "R" else t_mapping[home_slot[1]])
            a_team= winners[away_slot[1]] if away_slot[0] == "W" else (runners_up[away_slot[1]] if away_slot[0] == "R" else t_mapping[away_slot[1]])
            r32_matches.append((h_team, a_team))

        r32_winners= self._simulate_knockout_round(r32_matches, self.r32_dates, team_features, h2h_history)

        r16_matches= [(r32_winners[h], r32_winners[a]) for h, a in self.r16_pairs]
        r16_winners= self._simulate_knockout_round(r16_matches, self.r16_dates, team_features, h2h_history)

        qf_matches= [(r16_winners[h], r16_winners[a]) for h, a in self.qf_pairs]
        qf_winners= self._simulate_knockout_round(qf_matches, self.qf_dates, team_features, h2h_history)

        sf_matches= [(qf_winners[h], qf_winners[a]) for h, a in self.sf_pairs]
        sf_winners= self._simulate_knockout_round(sf_matches, self.sf_dates, team_features, h2h_history)

        final_winner= self._simulate_knockout_round([(sf_winners[0], sf_winners[1])], [self.final_date], team_features, h2h_history)[0]

        return {
            "group_stage": advanced,
            "r32_winners": r32_winners,
            "r16_winners": r16_winners,
            "qf_winners": qf_winners,
            "sf_winners": sf_winners,
            "champion": final_winner,
        }

    def run_monte_carlo(
        self, 
        groups, 
        team_features, 
        h2h_history, 
        output_dir,
        n_simulations=100, 
        seed=8, 
        db_engine=None,
        table_name="simulation_results",
        if_exists="replace"
    ):
        np.random.seed(seed)
        all_teams= [t for teams in groups.values() for t in teams]
        counts= {t: {"group_stage": 0, "r32": 0, "r16": 0, "qf": 0, "sf": 0, "champion": 0} for t in all_teams}

        for _ in range(n_simulations):
            tf_copy = {k: v.copy() for k, v in team_features.items()}
            res= self.simulate_single_tournament(groups, tf_copy, h2h_history)
            for t in res["group_stage"]: counts[t]["group_stage"] += 1
            for t in res["r32_winners"]: counts[t]["r32"] += 1
            for t in res["r16_winners"]: counts[t]["r16"] += 1
            for t in res["qf_winners"]: counts[t]["qf"] += 1
            for t in res["sf_winners"]: counts[t]["sf"] += 1
            counts[res["champion"]]["champion"] += 1

        rows= []
        for team, c in counts.items():
            rows.append({
                "team": team,
                "group_stage%": round(100 * c["group_stage"] / n_simulations, 2),
                "r32%": round(100 * c["r32"] / n_simulations, 2),
                "r16%": round(100 * c["r16"] / n_simulations, 2),
                "qf%": round(100 * c["qf"] / n_simulations, 2),
                "sf%": round(100 * c["sf"] / n_simulations, 2),
                "champion%": round(100 * c["champion"] / n_simulations, 2),
            })

        results_df= pd.DataFrame(rows).sort_values("champion%", ascending=False).reset_index(drop=True)
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            results_df.to_csv(os.path.join(output_dir, "monte_carlo_predictions.csv"), index=False)
        if db_engine is not None:
            sql_df = results_df.rename(columns={
                "group_stage%": "group_stage_pct",
                "r32%": "r32_pct",
                "r16%": "r16_pct",
                "qf%": "qf_pct",
                "sf%": "sf_pct",
                "champion%": "champion_pct",
            })
            sql_df["simulated_at"] = pd.Timestamp.now()
            sql_df["n_simulations"] = n_simulations
            sql_df.to_sql(
                name=table_name,
                con=db_engine,
                if_exists=if_exists,
                index=False
            )
        return results_df