package com.hermes.originservice;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@RestController
public class AssetController {
    @GetMapping("/api/v1/assets/{assetId}")
    public Map<String, String> getAsset(@PathVariable String assetId) throws InterruptedException {
        // Simulate a heavy database lookup or image processing
        Thread.sleep(3000);

        return Map.of(
                "assetId", assetId,
                "data", "This is the heavy payload for " + assetId,
                "source", "CORE_ORIGIN",
                "timestamp", String.valueOf(System.currentTimeMillis())
        );
    }
}