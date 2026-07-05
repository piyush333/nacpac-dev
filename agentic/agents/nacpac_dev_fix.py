# Replace the result_msg line in build_apk function
# Change this:
# result_msg = f"APK built successfully (commit: {commit[:8]}). Backups: R2={backup_results['r2']}, GDrive={backup_results['gdrive']}"

# To this:
backup_str = f"Backups: R2={backup_results.get('r2', 'N/A')}, GDrive={backup_results.get('gdrive', 'N/A')}" if backup_results else "Backups: Not configured"
result_msg = f"APK built successfully (commit: {commit[:8]}). {backup_str}"
