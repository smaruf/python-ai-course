package com.example.aidocprocessor

import android.app.Activity
import android.app.Instrumentation.ActivityResult
import android.content.Intent
import android.widget.Button
import android.widget.ListView
import android.widget.TextView
import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.intent.Intents
import androidx.test.espresso.intent.matcher.IntentMatchers.hasAction
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*

class UiFlow : AutoCloseable {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    lateinit var scenario: ActivityScenario<MainActivity>
    fun start() {
        instrumentation.targetContext.deleteDatabase("documents.db")
        Intents.init()
        scenario = ActivityScenario.launch(MainActivity::class.java)
        waitReady()
    }
    fun waitReady() {
        val deadline = System.currentTimeMillis() + 15_000
        while (System.currentTimeMillis() < deadline) {
            var ready = false
            scenario.onActivity { ready = it.findViewById<Button>(R.id.import_button).isEnabled }
            if (ready) { instrumentation.waitForIdleSync(); return }
            Thread.sleep(50)
        }
        fail("UI operation did not finish within 15 seconds")
    }
    fun importDocument(empty: Boolean = false) {
        Intents.intending(hasAction(Intent.ACTION_OPEN_DOCUMENT)).respondWith(
            ActivityResult(Activity.RESULT_OK, Intent().setData(if (empty) FixtureProvider.URI.buildUpon().path("empty").build() else FixtureProvider.URI))
        )
        onView(withId(R.id.import_button)).perform(click())
        waitReady()
    }
    fun assertStored() {
        scenario.onActivity { assertEquals(1, it.findViewById<ListView>(R.id.document_list).count) }
        onView(withId(R.id.document_detail)).check(matches(withSubstring("sapphire marker")))
    }
    fun restart() { scenario.close(); scenario = ActivityScenario.launch(MainActivity::class.java); waitReady() }
    fun viewDocument() {
        scenario.onActivity { activity ->
            val list = activity.findViewById<ListView>(R.id.document_list)
            list.performItemClick(list.getChildAt(0), 0, list.adapter.getItemId(0))
        }
        waitReady()
        onView(withId(R.id.document_detail)).check(matches(withSubstring("Extractive summary")))
    }
    fun search(query: String, expected: Int) {
        onView(withId(R.id.search_input)).perform(replaceText(query), closeSoftKeyboard())
        onView(withId(R.id.search_button)).perform(click())
        waitReady()
        scenario.onActivity { assertEquals(expected, it.findViewById<ListView>(R.id.document_list).count) }
    }
    fun delete() {
        onView(withId(R.id.delete_button)).perform(click())
        waitReady()
        scenario.onActivity { assertEquals(0, it.findViewById<ListView>(R.id.document_list).count) }
        DocumentStore(instrumentation.targetContext).use { assertTrue(it.list().isEmpty()) }
    }
    fun assertImportFailed() {
        scenario.onActivity {
            assertEquals(0, it.findViewById<ListView>(R.id.document_list).count)
            assertTrue(it.findViewById<TextView>(R.id.status).text.contains("failed"))
        }
    }
    fun askWithoutModel() {
        onView(withId(R.id.assistant_button)).perform(click())
        onView(withId(R.id.assistant_question)).perform(scrollTo(), replaceText("What is this document about?"), closeSoftKeyboard())
        onView(withId(R.id.assistant_answer_button)).perform(scrollTo(), click())
        waitReady()
        onView(withId(R.id.assistant_answer)).perform(scrollTo())
            .check(matches(withSubstring("Import a compatible local .task or .bin model first.")))
        DocumentStore(instrumentation.targetContext).use {
            assertEquals(1, it.list().size)
            assertEquals(FixtureProvider.FIXTURE_TEXT, it.get(it.list().first().first)!!.text)
        }
        onView(withText("Close")).perform(click())
    }
    override fun close() {
        if (::scenario.isInitialized) scenario.close()
        Intents.release()
        instrumentation.targetContext.deleteDatabase("documents.db")
    }
}
