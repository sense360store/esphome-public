#!/bin/bash
# Quick check for common duplicate entity issues in ESPHome configs

echo "🔍 Checking for duplicate entity definitions..."
echo ""

errors_found=0

# Check for restart entities
echo "1. Checking for duplicate Restart entities..."
restart_count=$(grep -rn "name:.*Restart" features/ hardware/ products/ --include="*.yaml" | grep -v "Restart LD" | wc -l)
if [ "$restart_count" -gt 10 ]; then
    echo "   ⚠️  Warning: Found $restart_count Restart entities (expected ~10)"
    grep -rn "name:.*Restart\"" features/ hardware/ products/ --include="*.yaml" | grep -v "Restart LD"
    errors_found=$((errors_found + 1))
else
    echo "   ✅ Restart entities look good ($restart_count found)"
fi

# Check for safe mode entities
echo ""
echo "2. Checking for duplicate Safe Mode entities..."
safe_mode_count=$(grep -rn "name:.*Safe Mode" features/ hardware/ products/ --include="*.yaml" | wc -l)
if [ "$safe_mode_count" -gt 2 ]; then
    echo "   ⚠️  Warning: Found $safe_mode_count Safe Mode entities (expected ~2 in hardware)"
    grep -rn "name:.*Safe Mode" features/ hardware/ products/ --include="*.yaml"
    errors_found=$((errors_found + 1))
else
    echo "   ✅ Safe Mode entities look good ($safe_mode_count found)"
fi

# Check device_health.yaml for conflicting entities
echo ""
echo "3. Checking device_health.yaml for conflicting entities..."
if grep -q "platform: restart" features/device_health.yaml 2>/dev/null; then
    echo "   ❌ ERROR: device_health.yaml still has switch.restart!"
    errors_found=$((errors_found + 1))
else
    echo "   ✅ No restart switch in device_health.yaml"
fi

if grep -q "platform: uptime" features/device_health.yaml 2>/dev/null; then
    echo "   ⚠️  Warning: device_health.yaml has duplicate uptime sensor"
    errors_found=$((errors_found + 1))
else
    echo "   ✅ No duplicate uptime in device_health.yaml"
fi

echo ""
echo "========================================"
if [ $errors_found -eq 0 ]; then
    echo "✅ All checks passed!"
    exit 0
else
    echo "❌ Found $errors_found issue(s)"
    exit 1
fi
