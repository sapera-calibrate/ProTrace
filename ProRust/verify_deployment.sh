#!/bin/bash
# Verify ProTRACE Deployment on Solana Devnet

PROGRAM_ID="7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG"
CLUSTER="devnet"

echo "=================================================="
echo "🔍 Verifying ProTRACE Deployment"
echo "=================================================="
echo ""
echo "Program ID: $PROGRAM_ID"
echo "Cluster: $CLUSTER"
echo ""

# Test 1: Check program exists
echo "✅ Test 1: Program Existence"
solana program show $PROGRAM_ID --url $CLUSTER
echo ""

# Test 2: Check program account
echo "✅ Test 2: Program Account"
solana account $PROGRAM_ID --url $CLUSTER
echo ""

# Test 3: Fetch IDL
echo "✅ Test 3: IDL Verification"
cd ~/ProRust-deploy
anchor idl fetch $PROGRAM_ID --provider.cluster $CLUSTER > /tmp/fetched_idl.json 2>/dev/null
if [ -f /tmp/fetched_idl.json ]; then
    echo "✅ IDL fetched successfully"
    cat /tmp/fetched_idl.json | jq '.instructions[] | .name'
else
    echo "⚠️  IDL not yet indexed (this is normal immediately after deployment)"
fi
echo ""

# Test 4: Check local IDL
echo "✅ Test 4: Local IDL"
if [ -f ~/ProRust-deploy/target/idl/protrace.json ]; then
    echo "✅ Local IDL exists"
    echo "Available instructions:"
    cat ~/ProRust-deploy/target/idl/protrace.json | jq '.instructions[] | .name'
else
    echo "❌ Local IDL not found"
fi
echo ""

# Test 5: Check program binary
echo "✅ Test 5: Program Binary"
if [ -f ~/ProRust-deploy/target/deploy/protrace.so ]; then
    PROGRAM_SIZE=$(du -h ~/ProRust-deploy/target/deploy/protrace.so | cut -f1)
    echo "✅ Program binary exists: $PROGRAM_SIZE"
else
    echo "❌ Program binary not found"
fi
echo ""

# Test 6: Verify configuration files
echo "✅ Test 6: Configuration Files"
if grep -q "$PROGRAM_ID" ~/ProRust-deploy/Anchor.toml; then
    echo "✅ Anchor.toml updated"
else
    echo "⚠️  Anchor.toml needs update"
fi

if grep -q "$PROGRAM_ID" "/mnt/d/ProTRACE - Copy - Copy/ProTRACE/shared/config/testsprite.config.json"; then
    echo "✅ TestSprite config updated"
else
    echo "⚠️  TestSprite config needs update"
fi
echo ""

echo "=================================================="
echo "✅ Verification Complete"
echo "=================================================="
echo ""
echo "🔗 Quick Links:"
echo "  - Explorer: https://explorer.solana.com/address/$PROGRAM_ID?cluster=$CLUSTER"
echo "  - Program Info: solana program show $PROGRAM_ID --url $CLUSTER"
echo "  - Fetch IDL: anchor idl fetch $PROGRAM_ID --provider.cluster $CLUSTER"
echo ""
echo "🎯 Next Steps:"
echo "  1. Run integration tests"
echo "  2. Test each instruction"
echo "  3. Update client applications"
echo "  4. Re-run TestSprite tests"
echo ""
