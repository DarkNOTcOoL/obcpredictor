# obcpredictor
## [RELEASE] JEE Percentile ⇄ OBC Rank Predictor

## [UPDATE 1] JEE Rank Predictor: Now with support for General, OBC, & EWS

## [UPDATE 2] Started to use numpy.interp() function instead of previous method




I’ve completely overhauled the logic to support General and EWS categories alongside OBC-NCL.

If you're tired of websites that give you a single random number out of thin air with no context, try this.

It uses dynamic data mapping to interpolate ratios based on your specific percentile bracket, you can have a look under the hood how the calculations work n shi for yourself

you don't need to give your response sheet/reg no. or anything... just type in ur percentile

Try it here: [ https://rankpredictor.streamlit.app/ ]

---------------------------------------------------------------------------------------------------------------

## What’s New?
Multi-Category Support: Full integration for General, OBC-NCL, and EWS ranks.

Dynamic Ratios: No fixed multipliers. The app automatically adjusts the Category-to-CRL ratio based on where you sit in the percentile curve.

Full Transparency: Every calculation shows the exact formula and intermediate CRL (All India Rank) used. No hidden math.

Bidirectional Conversion: Instantly flip between Percentile → Rank or Rank → Percentile.

Custom Parameters: You can manually tweak the total unique candidates or adjust Conservative/Optimistic ratios in the sidebar to stress-test your results.

----------------------------------------------------------------------

## College & Placement Insights (only for OBC):
NIT CSE Predictor: Instantly matches your predicted rank against cutoff data for NIT Computer Science branches.

Placement Data: Displays the Mean CSE Package (LPA) for the colleges you qualify for.

Modern UI: Fast, responsive, and actually looks good (no AI-generated UI slop).

-------------------------------------------------------------------------------------------

*Open to feedback and constructive criticism. Calculations are based on updated 2026 trends and candidate estimates.*
