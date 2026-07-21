"""Orchestrator for routing requests to appropriate agents."""

import os
from datetime import datetime
from sqlalchemy import text
from agent import Agent, AgentConfig, create_developer_agent


class Orchestrator:
    """Routes requests to appropriate agents and manages execution."""

    def __init__(self):
        self.developer_agent = create_developer_agent()

    async def execute(self, user_input: str, project_id: str, db) -> dict:
        """
        Execute a user request:
        1. Save request to DB
        2. Route to appropriate agent
        3. Execute agent
        4. Save response to DB
        5. Return result
        """
        try:
            # Insert request into DB
            result = db.execute(
                text("""
                    INSERT INTO requests (project_id, user_input, status, created_at)
                    VALUES (:project_id, :user_input, 'running', :created_at)
                    RETURNING id
                """),
                {
                    "project_id": project_id,
                    "user_input": user_input,
                    "created_at": datetime.utcnow()
                }
            )
            db.commit()
            request_id = result.fetchone()[0]

            # Execute agent (currently just developer agent for Phase 1)
            agent_result = self.developer_agent.execute(user_input)

            if not agent_result.get("success"):
                response_text = f"Error: {agent_result.get('error', 'Unknown error')}"
                status = "failed"
            else:
                response_text = agent_result.get("response", "")
                status = "completed"

            tokens_used = agent_result.get("tokens_used", 0)
            estimated_cost = self._estimate_cost(
                agent_result.get("input_tokens", 0),
                agent_result.get("output_tokens", 0)
            )

            # Update request with response
            db.execute(
                text("""
                    UPDATE requests
                    SET response = :response,
                        status = :status,
                        tokens_used = :tokens_used,
                        estimated_cost = :estimated_cost,
                        completed_at = :completed_at
                    WHERE id = :id
                """),
                {
                    "id": request_id,
                    "response": response_text,
                    "status": status,
                    "tokens_used": tokens_used,
                    "estimated_cost": estimated_cost,
                    "completed_at": datetime.utcnow()
                }
            )
            db.commit()

            return {
                "request_id": request_id,
                "status": status,
                "response": response_text,
                "tokens_used": tokens_used,
                "estimated_cost": estimated_cost
            }

        except Exception as e:
            # Log error and update request status
            try:
                db.execute(
                    text("""
                        UPDATE requests
                        SET status = 'error',
                            response = :error_msg,
                            completed_at = :completed_at
                        WHERE id = :id
                    """),
                    {
                        "id": request_id if 'request_id' in locals() else None,
                        "error_msg": str(e),
                        "completed_at": datetime.utcnow()
                    }
                )
                db.commit()
            except:
                pass

            raise

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on token usage (Claude 3.5 Sonnet pricing)."""
        # Claude 3.5 Sonnet: $3/1M input tokens, $15/1M output tokens
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return round(input_cost + output_cost, 6)


# Singleton orchestrator instance
orchestrator = Orchestrator()
