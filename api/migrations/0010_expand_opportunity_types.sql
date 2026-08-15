-- Preserve existing Opportunity records while allowing additional detector types.

ALTER TABLE opportunities DROP CONSTRAINT opportunities_opportunity_type_check;

ALTER TABLE opportunities
    ADD CONSTRAINT opportunities_opportunity_type_check
    CHECK (opportunity_type IN (
        'LOW_DEMAND_SLOT',
        'CANCELLATION_HOTSPOT',
        'DORMANT_CUSTOMER',
        'SERVICE_DEMAND_GAP'
    ));
