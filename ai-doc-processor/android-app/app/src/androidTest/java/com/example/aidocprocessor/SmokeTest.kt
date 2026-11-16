package com.example.aidocprocessor

import android.Manifest
import android.content.pm.PackageManager
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class SmokeTest {
    @Test fun launchesWithoutNetworkPermission() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals(PackageManager.PERMISSION_DENIED, context.packageManager.checkPermission(Manifest.permission.INTERNET, context.packageName))
        ActivityScenario.launch(MainActivity::class.java).use {
            onView(withId(R.id.import_button)).check(matches(isDisplayed()))
            onView(withId(R.id.search_button)).check(matches(isDisplayed()))
        }
    }
}
