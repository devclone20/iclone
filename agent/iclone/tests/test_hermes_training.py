"""
TDD — Hermes Training Test Suite
Validates iCLONE's knowledge of full Hermes + ACP CLI command set.
"""

import pytest
from agent.iclone.training.hermes_training import HermesTraining


@pytest.fixture
def hermes():
    return HermesTraining()


class TestButlerCommands:

    def test_reset_command_known(self, hermes):
        assert "/reset" in hermes.BUTLER_COMMANDS

    def test_topup_command_known(self, hermes):
        assert "/topup <amount>" in hermes.BUTLER_COMMANDS


class TestACPCLI:

    def test_binary_is_acp(self, hermes):
        assert hermes.ACP_CLI["binary"] == "acp"

    def test_json_flag_known(self, hermes):
        assert "--json" in hermes.ACP_CLI["global_flags"]

    def test_wallet_commands_present(self, hermes):
        wallet = hermes.ACP_CLI["wallet"]
        assert "acp wallet address" in wallet
        assert "acp wallet balance --chain-id ID" in wallet

    def test_email_commands_minimum(self, hermes):
        email = hermes.ACP_CLI["email"]
        assert "acp email whoami" in email
        assert "acp email compose" in email
        assert "acp email inbox" in email

    def test_virtual_cards_known(self, hermes):
        cards = hermes.ACP_CLI["virtual_cards"]
        assert "acp card issue --amount CENTS" in cards
        assert "acp card list" in cards

    def test_marketplace_browse_known(self, hermes):
        assert "acp browse QUERY" in hermes.ACP_CLI["marketplace"]

    def test_offering_crud_known(self, hermes):
        offerings = hermes.ACP_CLI["offerings"]
        assert "acp offering create" in offerings
        assert "acp offering list" in offerings
        assert "acp offering update" in offerings
        assert "acp offering delete" in offerings

    def test_client_job_lifecycle_known(self, hermes):
        client = hermes.ACP_CLI["client_jobs"]
        assert "acp client create-job" in client
        assert "acp client fund" in client
        assert "acp client complete" in client

    def test_provider_job_lifecycle_known(self, hermes):
        provider = hermes.ACP_CLI["provider_jobs"]
        assert "acp provider submit" in provider
        assert "acp provider set-budget" in provider

    def test_events_commands_known(self, hermes):
        events = hermes.ACP_CLI["events"]
        assert "acp events listen" in events
        assert "acp events drain --file FILE" in events

    def test_subscriptions_known(self, hermes):
        subs = hermes.ACP_CLI["subscriptions"]
        assert "acp subscription create" in subs
        assert "acp subscription list" in subs


class TestDegenClaw:

    def test_schedule_is_12h(self, hermes):
        assert "12" in hermes.DEGENCLAW["schedule"]

    def test_trading_commands_known(self, hermes):
        trading = hermes.DEGENCLAW["trading"]
        assert "open_position" in trading
        assert "close_position" in trading
        assert "balance" in trading
        assert "positions" in trading

    def test_forum_post_command_known(self, hermes):
        forum = hermes.DEGENCLAW["forum"]
        assert "dgclaw.sh create-post" in " ".join(forum.keys())

    def test_deposit_uses_correct_provider(self, hermes):
        deposit = hermes.DEGENCLAW["deposits_withdrawals"]["deposit"]
        assert "0xd478a8B40372db16cA8045F28C6FE07228F3781A" in deposit
        assert "perp_deposit" in deposit

    def test_leaderboard_known(self, hermes):
        lb = hermes.DEGENCLAW["leaderboard"]
        assert "dgclaw.sh leaderboard" in lb


class TestHermesCLI:

    def test_binary_is_hermes(self, hermes):
        assert hermes.HERMES_CLI["binary"] == "hermes"

    def test_chat_commands_known(self, hermes):
        chat = hermes.HERMES_CLI["chat"]
        assert "hermes chat" in chat
        assert "hermes -z '<prompt>'" in chat

    def test_acp_integration_known(self, hermes):
        assert "hermes acp" in hermes.HERMES_CLI["acp_integration"]

    def test_cron_commands_known(self, hermes):
        automation_keys = " ".join(hermes.HERMES_CLI["automation"].keys())
        assert "hermes cron" in automation_keys


class TestHermesSlash:

    def test_new_session_command_known(self, hermes):
        assert "/new" in hermes.HERMES_SLASH["session_management"]

    def test_background_command_known(self, hermes):
        assert "/background <prompt>" in hermes.HERMES_SLASH["session_management"]

    def test_status_gateway_only(self, hermes):
        assert "/status" in hermes.HERMES_SLASH["session_management"]
        assert "Gateway only" in hermes.HERMES_SLASH["session_management"]["/status"]

    def test_provider_command_known(self, hermes):
        assert "/provider" in hermes.HERMES_SLASH["configuration"]

    def test_prompt_command_known(self, hermes):
        assert "/prompt [text]" in hermes.HERMES_SLASH["configuration"]

    def test_cron_command_known(self, hermes):
        assert "/cron [subcommand]" in hermes.HERMES_SLASH["tools_skills"]

    def test_browser_command_known(self, hermes):
        assert "/browser [connect|disconnect|status]" in hermes.HERMES_SLASH["tools_skills"]

    def test_quit_command_known(self, hermes):
        assert "/quit" in hermes.HERMES_SLASH["info"]

    def test_insights_command_known(self, hermes):
        assert "/insights [days]" in hermes.HERMES_SLASH["info"]

    def test_update_gateway_only(self, hermes):
        assert "/update" in hermes.HERMES_SLASH["info"]
        assert "Gateway only" in hermes.HERMES_SLASH["info"]["/update"]

    def test_four_sections_exist(self, hermes):
        assert len(hermes.HERMES_SLASH) == 4


class TestACPV2:

    def test_seven_event_types(self, hermes):
        assert len(hermes.ACP_V2["events"]["event_names"]) == 7

    def test_job_completed_event_known(self, hermes):
        assert "job.completed" in hermes.ACP_V2["events"]["event_names"]

    def test_python_sdk_known(self, hermes):
        sdk = hermes.ACP_V2["python_sdk"]
        assert "initiate_job" in sdk
        assert "deliver_job" in sdk
        assert "browse" in sdk


class TestDeprecated:

    def test_game_sdk_deprecated(self, hermes):
        assert "game-sdk" in hermes.DEPRECATED

    def test_game_api_key_deprecated(self, hermes):
        assert "GAME_API_KEY" in hermes.DEPRECATED

    def test_acp_buyer_deprecated(self, hermes):
        assert "acp buyer *" in hermes.DEPRECATED


class TestCriticalCommands:

    def test_daily_trading_commands_defined(self, hermes):
        assert len(hermes.ICLONE_CRITICAL["daily_trading_cycle"]) >= 5

    def test_forum_post_in_daily_cycle(self, hermes):
        daily = " ".join(hermes.ICLONE_CRITICAL["daily_trading_cycle"])
        assert "create-post" in daily

    def test_acp_job_lifecycle_commands_defined(self, hermes):
        assert len(hermes.ICLONE_CRITICAL["acp_job_lifecycle"]) >= 3

    def test_identity_check_commands_defined(self, hermes):
        assert len(hermes.ICLONE_CRITICAL["identity_check"]) == 3


class TestTrainingSession:

    def test_session_completes(self, hermes):
        result = hermes.run_session("test_hermes_001")
        assert result["completed"] is True

    def test_session_has_insights(self, hermes):
        result = hermes.run_session("test_hermes_002")
        assert result["insights_count"] >= 15

    def test_session_has_command_groups(self, hermes):
        result = hermes.run_session("test_hermes_003")
        assert result["command_groups"] >= 10

    def test_session_has_slash_commands(self, hermes):
        result = hermes.run_session("test_hermes_004")
        assert result["slash_commands"] >= 30

    def test_session_knows_deprecated(self, hermes):
        result = hermes.run_session("test_hermes_005")
        assert result["deprecated_known"] >= 5

    def test_session_has_timestamp(self, hermes):
        result = hermes.run_session("test_hermes_006")
        assert "timestamp" in result
