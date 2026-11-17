package com.example.aidocprocessor

import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Test
import org.junit.Assume.assumeFalse
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class DocumentE2ETest {
    @Test fun importPersistViewSearchDeleteThroughUi() {
        UiFlow().use { flow ->
            flow.start(); flow.importDocument(); flow.assertStored()
            flow.restart(); flow.viewDocument()
            flow.search("sapphire", 1); flow.search("not-in-document", 0); flow.search("", 1)
            flow.delete(); flow.restart(); flow.search("", 0)
        }
    }
    @Test fun emptyImportReportsErrorWithoutPersisting() {
        UiFlow().use { flow -> flow.start(); flow.importDocument(empty = true); flow.assertImportFailed() }
    }
    @Test fun missingModelIsReportedWithoutFallbackOrDocumentLoss() {
        val context = androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().targetContext
        LocalAssistant(context).use { assumeFalse("Run the missing-model scenario on a fresh installation", it.hasModel()) }
        UiFlow().use { flow -> flow.start(); flow.importDocument(); flow.askWithoutModel(); flow.assertStored() }
    }
}
