Feature: Offline document lifecycle
  Scenario: Import and rediscover a local document
    Given an empty local document library
    When I import a UTF-8 document
    Then the summary and extracted text are visible
    When I restart the app
    And I open the stored document
    Then searching for sapphire finds one document
    And searching for absent finds no documents
    When I clear the search
    And I delete the selected document
    Then the library remains empty after restart

  Scenario: Reject empty input
    Given an empty local document library
    When I import an empty document
    Then an error appears and nothing is stored

  Scenario: Local assistant requires an imported model
    Given an empty local document library
    And no local LLM model is installed
    When I import a UTF-8 document
    And I ask the local assistant about the document
    Then the missing model is explained and the document is retained
