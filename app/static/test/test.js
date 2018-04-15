// need a global _ because recs depends on it
_ = require("../js/lib/underscore.min");

const assert = require("assert");
const recs = require("../js/recs");

describe("Recommendations", function() {
  describe("#addExpectation()", () =>
    it("should be empty object", () => assert.ok(_.isEmpty(recs.addExpectation([], []))))
  );

  describe("#getRecommended()", () =>
    it("should be empty array", () => assert.equal(recs.getRecommended({}).length, 0))
  );

  describe("#checkExpectations()", () =>
    it("should be empty object", () => assert.ok(_.isEmpty(recs.checkExpectations(null, {}))))
  );

  describe("#addExpectation()", () =>
    it("should add positive expectation", function() {
      let E = {};
      E = recs.addExpectation(["1"], []);
      // E should be {1: true}
      assert.ok(E[1]);
    })
  );

  describe("#addExpectation()", () =>
    it("should add two expectations", function() {
      const E = recs.addExpectation(["1"], ["2"]);
      // E should be {1: true, 2: false}
      assert.ok(E[1]);
      assert.equal(E[2], false);
    })
  );

  describe("#checkRelations()", () =>
    it("should remain the same", function() {
      const E = recs.addExpectation(["1"], []);
      // E is now {1: true}
      const is_checked = true;
      // expectations are met because is_checked is true
      assert.ok(recs.checkExpectations(is_checked, E)[1]);
    })
  );

  describe("#checkRelations()", () =>
    it("should differ from reality", function() {
      const E = recs.addExpectation(["1"], []);
      // E is now {1: true}
      const is_checked = false;
      // expections are not met because is_checked is false
      assert.equal(recs.checkExpectations(is_checked, E)[1], false);
    })
  );
});
