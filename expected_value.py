def expected_stat(
    minutes_proj,
    stat_per_min,
    recent_form_adj,
    usage_adj,
    opp_def_adj,
    pace_adj,
    home_adj
):
    return (
        minutes_proj
        * stat_per_min
        * recent_form_adj
        * usage_adj
        * opp_def_adj
        * pace_adj
        * home_adj
    )
