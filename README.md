# obcpredictor
## [RELEASE] JEE Percentile ⇄ OBC Rank Predictor

## [UPDATE 1] JEE Rank Predictor: Now with support for General, OBC, & EWS

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

## [UPDATE 2] Started to use numpy.interp() function instead of previous method

## [UPDATE 3] Added graphs for visual representation (taaki logo ko na lage hawa bazi mein prediction chal rhi hao

-------------------------------------------------------------------------------------------
## flexing my stats:
<img width="1568" height="708" alt="Screenshot 2026-04-13 224923" src="https://github.com/user-attachments/assets/523648e7-b095-43e1-8386-8b1c6a317f3f" />
<img width="1723" height="711" alt="Screenshot 2026-04-17 193800" src="https://github.com/user-attachments/assets/8f24972e-61d0-4229-a2ff-1feab35d6a9e" />
<img width="519" height="337" alt="Screenshot 2026-04-17 190625" src="https://github.com/user-attachments/assets/1fe4e36b-e0c1-46fd-98c4-45ae6ab6286f" />
managed to hit 4.52k+ page views, 30.11+ script runs and 768+ unique visitors in less than 10 days 

-------------------------------------------------------------------------------------------

*Open to feedback and constructive criticism. Calculations are based on updated 2026 trends and candidate estimates.*
