"""Deploy and test script for yc-companies-founders-scraper."""
import json
import os
import sys
import time

sys.path.insert(0, "/Users/kamerozkan/.gemini/antigravity/scratch/apify-operator/tools")
from apify import call, data, get

ACTOR_NAME = "yc-companies-founders-scraper"
ACTOR_TITLE = "Y Combinator Companies & Founders Scraper"
ACTOR_DESCRIPTION = (
    "Ultra-fast, browserless Y Combinator scraper. Extract company profiles, tech tags, "
    "team metrics, hiring signals, and founder LinkedIn profiles directly via official APIs."
)
PROJECT_DIR = "/Users/kamerozkan/.gemini/antigravity/scratch/yc-companies-founders-scraper"


def collect_source_files():
    files = []
    ignored = {"deploy_and_test.py", ".DS_Store", "test_run.py"}
    for root, _, filenames in os.walk(PROJECT_DIR):
        for fname in sorted(filenames):
            if fname in ignored or fname.endswith(".pyc"):
                continue
            if fname.startswith(".") and fname not in [".actor"]:
                continue
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, PROJECT_DIR)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            files.append({
                "name": rel_path,
                "format": "TEXT",
                "content": content
            })
    return files


def main():
    print(f"=== Deploying {ACTOR_NAME} ===")
    source_files = collect_source_files()
    print(f"Collected {len(source_files)} files:")
    for f in source_files:
        print(f"  - {f['name']} ({len(f['content'])} bytes)")

    # 1. Check if actor already exists or create new
    existing_actors = {a["name"]: a["id"] for a in data("/acts?my=1&limit=1000")["items"]}
    if ACTOR_NAME in existing_actors:
        act_id = existing_actors[ACTOR_NAME]
        print(f"Actor exists: ID={act_id}. Ensuring it is PRIVATE...")
        st, res = call("PUT", f"/acts/{act_id}", body={"isPublic": False})
        print(f"Updated actor isPublic=False: HTTP {st}")
    else:
        st, res = call("POST", "/acts", body={
            "name": ACTOR_NAME,
            "title": ACTOR_TITLE,
            "description": ACTOR_DESCRIPTION,
            "isPublic": False
        })
        if st not in (200, 201):
            raise RuntimeError(f"Failed to create actor: HTTP {st} {res}")
        act_id = res["data"]["id"]
        print(f"Created new PRIVATE actor: ID={act_id}")

    # 2. Upload source files to version 1.0
    payload = {
        "versionNumber": "1.0",
        "sourceType": "SOURCE_FILES",
        "sourceFiles": source_files,
        "buildTag": "latest"
    }
    versions_list = data(f"/acts/{act_id}/versions")["items"]
    v_nums = [v["versionNumber"] for v in versions_list]
    if "1.0" in v_nums:
        st, res = call("PUT", f"/acts/{act_id}/versions/1.0", body=payload)
    else:
        st, res = call("POST", f"/acts/{act_id}/versions", body=payload)
    if st not in (200, 201):
        raise RuntimeError(f"Failed to upload version 1.0: HTTP {st} {res}")
    print(f"Source files uploaded to version 1.0 (HTTP {st})")

    # 3. Configure Pay-Per-Event pricing ($0.003 / item)
    pricing_payload = {
        "pricingModel": "PAY_PER_EVENT",
        "pricingPerEvent": {
            "actorChargeEvents": {
                "yc-record": {
                    "eventTitle": "Extracted YC Record",
                    "eventDescription": "Charged per extracted YC company or founder record with full profiles and socials.",
                    "eventPriceUsd": 0.003,
                    "isPrimaryEvent": True
                }
            }
        }
    }
    st_p, res_p = call("POST", f"/acts/{act_id}/pricing-infos", body=pricing_payload)
    print(f"Configured Pay-Per-Event pricing ($0.003/item): HTTP {st_p}")

    # 4. Trigger build
    st_b, b_res = call("POST", f"/acts/{act_id}/builds?version=1.0")
    if st_b not in (200, 201):
        raise RuntimeError(f"Failed to trigger build: HTTP {st_b} {b_res}")
    build_id = b_res["data"]["id"]
    build_num = b_res["data"]["buildNumber"]
    print(f"Build started: #{build_num} (ID: {build_id}). Waiting for completion...")

    # Wait for build to complete
    start_wait = time.time()
    while time.time() - start_wait < 300:
        b_info = data(f"/actor-builds/{build_id}")
        b_status = b_info.get("status")
        print(f"  Build status: {b_status} ({int(time.time() - start_wait)}s)")
        if b_status == "SUCCEEDED":
            print(f"Build #{build_num} SUCCEEDED!")
            break
        elif b_status in ("FAILED", "ABORTED", "TIMED-OUT"):
            log_st, log_txt = call("GET", f"/actor-builds/{build_id}/log", raw=True)
            print(f"BUILD FAILED LOG:\n{log_txt}")
            raise RuntimeError(f"Build failed with status: {b_status}")
        time.sleep(5)

    # 5. Execute isolated test run
    print("\n=== Executing Isolated Test Run ===")
    test_input = {
        "outputMode": "companies",
        "batches": ["Winter 2026"],
        "maxItems": 5,
        "includeDeepDetails": True
    }
    st_r, r_res = call("POST", f"/acts/{act_id}/runs?build=latest", body=test_input)
    if st_r not in (200, 201):
        raise RuntimeError(f"Failed to start test run: HTTP {st_r} {r_res}")
    run_id = r_res["data"]["id"]
    dataset_id = r_res["data"]["defaultDatasetId"]
    print(f"Test run started: ID={run_id}, DatasetID={dataset_id}. Waiting for completion...")

    start_wait = time.time()
    while time.time() - start_wait < 180:
        run_info = data(f"/actor-runs/{run_id}")
        r_status = run_info.get("status")
        print(f"  Run status: {r_status} ({int(time.time() - start_wait)}s)")
        if r_status == "SUCCEEDED":
            print(f"Test Run SUCCEEDED!")
            break
        elif r_status in ("FAILED", "ABORTED", "TIMED-OUT"):
            log_st, log_txt = call("GET", f"/actor-runs/{run_id}/log", raw=True)
            print(f"RUN FAILED LOG:\n{log_txt}")
            raise RuntimeError(f"Test run failed with status: {r_status}")
        time.sleep(4)

    # 6. Fetch and verify dataset items
    st_d, items = call("GET", f"/datasets/{dataset_id}/items")
    print(f"\nExtracted items count: {len(items)}")
    if len(items) > 0:
        print("Sample item 0:")
        print(json.dumps(items[0], indent=2)[:600])

    # 7. Execute zero-config test run (input = {})
    print("\n=== Executing Zero-Config Test Run (Input = {}) ===")
    st_z, z_res = call("POST", f"/acts/{act_id}/runs?build=latest", body={})
    if st_z not in (200, 201):
        raise RuntimeError(f"Failed to start zero-config run: HTTP {st_z} {z_res}")
    z_run_id = z_res["data"]["id"]
    z_dataset_id = z_res["data"]["defaultDatasetId"]
    print(f"Zero-config run started: ID={z_run_id}. Waiting...")

    start_wait = time.time()
    while time.time() - start_wait < 180:
        z_info = data(f"/actor-runs/{z_run_id}")
        z_status = z_info.get("status")
        print(f"  Zero-config run status: {z_status} ({int(time.time() - start_wait)}s)")
        if z_status == "SUCCEEDED":
            print(f"Zero-config run SUCCEEDED!")
            break
        elif z_status in ("FAILED", "ABORTED", "TIMED-OUT"):
            log_st, log_txt = call("GET", f"/actor-runs/{z_run_id}/log", raw=True)
            print(f"ZERO-CONFIG RUN FAILED LOG:\n{log_txt}")
            raise RuntimeError(f"Zero-config run failed with status: {z_status}")
        time.sleep(4)

    st_zd, z_items = call("GET", f"/datasets/{z_dataset_id}/items")
    print(f"Zero-config run extracted items count: {len(z_items)}")

    print("\nALL DEPLOYMENT AND TEST STEPS SUCCEEDED!")
    return {
        "act_id": act_id,
        "build_num": build_num,
        "run_id": run_id,
        "items_count": len(items),
        "zero_config_run_id": z_run_id,
        "zero_config_items": len(z_items)
    }


if __name__ == "__main__":
    main()
