# app.py
import math
import streamlit as st

st.set_page_config(page_title="Bungalow Block Estimator", page_icon="🧱")

st.title("🧱 Bungalow Block Estimation Tool")

# --- helper for currency formatting ---
def naira(amount: float) -> str:
    try:
        return f"₦{amount:,.2f}"
    except Exception:
        return f"₦{amount}"

# --- Instruction box ---
st.info(
    "### Instruction\n"
    "**Enter the total wall perimeter** of your bungalow.\n\n"
    "- Measure **all external walls** around the building.\n"
    "- If there are **courtyards, re-entrant corners, or projections**, include those lengths too.\n"
    "- To include **internal partitions / room walls**, **add their lengths to the perimeter** before entering it here.\n"
    "- Use the **average wall height**. If heights differ, consider splitting into segments and summing areas.\n\n"
    "Formula used: `Wall Area = Perimeter × Height`, then we subtract openings and divide by block face area."
)

with st.form("perimeter_form"):
    st.subheader("Inputs")

    # Perimeter method inputs
    P = st.number_input("Total perimeter (m)", min_value=0.0, step=0.1)
    H = st.number_input("Wall height (m)", min_value=0.0, step=0.1)

    st.markdown("**Block dimensions** (use nominal size incl. mortar if possible)")
    bl = st.number_input("Block length (m)", min_value=0.0, step=0.01)
    bh = st.number_input("Block height (m)", min_value=0.0, step=0.01)

    st.markdown("**Openings**")
    doors = st.number_input("Number of doors", min_value=0, step=1)
    dw = st.number_input("Door width (m)", min_value=0.0, step=0.01)
    dh = st.number_input("Door height (m)", min_value=0.0, step=0.01)

    windows = st.number_input("Number of windows", min_value=0, step=1)
    ww = st.number_input("Window width (m)", min_value=0.0, step=0.01)
    wh = st.number_input("Window height (m)", min_value=0.0, step=0.01)

    st.markdown("**Wastage & Cost**")
    wastage_pct = st.slider("Wastage allowance (%)", 0, 20, 5, help="Increase to 8–12% for curved walls.")
    unit_cost = st.number_input("Cost per block (₦)", min_value=0.0, step=10.0, help="Enter the price for one block.")

    submitted = st.form_submit_button("Estimate")

if submitted:
    # Validation
    if P <= 0 or H <= 0:
        st.error("Perimeter and wall height must be greater than 0.")
    elif bl <= 0 or bh <= 0:
        st.error("Block dimensions must be greater than 0.")
    else:
        # Calculations
        total_wall_area = P * H
        openings_area = doors * (dw * dh) + windows * (ww * wh)
        net_wall_area = max(total_wall_area - openings_area, 0.0)

        block_area = bl * bh
        raw_blocks = net_wall_area / block_area if block_area else 0.0
        final_blocks = math.ceil(raw_blocks * (1 + wastage_pct / 100))

        # Cost calculation in Naira
        total_cost = final_blocks * unit_cost

        # Results
        st.success("Calculation complete")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total Wall Area (m²)", f"{total_wall_area:.2f}")
            st.metric("Openings Area (m²)", f"{openings_area:.2f}")
            st.metric(f"Blocks (+{wastage_pct}%)", f"{final_blocks}")
        with c2:
            st.metric("Net Wall Area (m²)", f"{net_wall_area:.2f}")
            st.metric("Unit Cost (₦/block)", naira(unit_cost))
            st.metric("Total Cost (₦)", naira(total_cost))

        with st.expander("Details"):
            st.write({
                "block_face_area_m2": round(block_area, 4),
                "blocks_raw": int(raw_blocks),
                "assumptions": "Uniform height; openings subtracted; partitions included via perimeter; wastage applied.",
            })

st.caption("Tip: For split heights or inner courtyards, sum each segment's length × height and use that as your effective area.")
